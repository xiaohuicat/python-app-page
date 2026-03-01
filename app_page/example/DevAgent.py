import time
from PySide6.QtCore import QObject, Signal
from app_page import Page, getSetting
from app_page.utils import encode, call_qwen
from app_page.plugins import DevAgent as DevAgentPlugin

template = """
<template>
  <div class="container" margins="[10, 10, 10, 10]">
    <v-box spacing="10" margins="[0,0,0,0]">
      <label text="${title}" class="title"/>
      <div class="main-content">
        <h-box margins="[0,0,0,0]" >
          <line-edit 
            id="message" 
            text="" 
            style="border-radius:6px;"
            placeholder="请输入你想问AI智能体的问题..."
          />
          <button id="submit" text="发送" />
        </h-box>
      </div>
      <text-edit id="shell" text="${reply}" class="shell" />
    </v-box>
  </div>
</template>
"""

style = """
.container {
  background-color: rgba(255,255,255,0.6);
  border-radius: 10px;
}
.title {
  background-color: transparent;
  font-size: 22px;
  font-weight: bold;
}
.shell {
  color: #333;
  padding: 5px;
  border-radius: 6px;
  font-size: 14px;
  background-color: rgba(255,255,255,0.8);
}
.running {
  background-color: #45C8FC;
}
"""

mcp_dict = {
  "read_project": {
    "url": "http://127.0.0.1:8080/list_dir",
    "param": ["path"],
    "description": "读取本地项目目录的markdown结构树",
  },
  "read_file": {
    "url": "http://127.0.0.1:8080/read_file",
    "param": ["file_path"],
    "description": "读取本地文件内容，返回文件内容字符串"
  },
  "write_file": {
    "url": "http://127.0.0.1:8080/write_file",
    "param": ["file_path", "content"],
    "description": "写入内容到本地文件，path是文件路径，content是要写入的字符串内容"
  },
  "delete_file": {
    "url": "http://127.0.0.1:8080/delete_file",
    "param": ["file_path"],
    "description": "删除本地文件，path是文件路径"
  },
  "download_file": {
    "url": "http://127.0.0.1:8080/download_file",
    "param": ["url", "save_path"],
    "description": "下载文件到本地，url是文件链接，save_path是要保存的本地路径"
  },
  "system_info": {
    "url": "http://127.0.0.1:8080/system_info",
    "param": [],
    "description": "获取系统信息，如处理器型号、内存大小、硬盘使用情况等"
  },
  "get_weather": {
    "url": "http://127.0.0.1:8080/get_weather",
    "param": ['citycode'],
    "description": "获取天气信息，citycode是城市编码，北京是110101"
  },
  "draw_image": {
    "url": "http://127.0.0.1:8080/draw_image",
    "param": ['prompt', 'size'],
    "description": "根据提示词生成图像，prompt是提示词。size是图像大小，支持1328*1328"
  },
}

BLOCK_LINE = '\r\n\r\n'

def convert_messages(messages):
  result = ""
  for item in messages:
    head = BLOCK_LINE if result else ""
    if item['role'] == 'system':
      continue
      result += f"💻system: {item['content']}"
    elif item['role'] == 'user':
      result += f"{head}👨user: {item['content']}"
    else:
      result += f"{head}🤖assistant: {item['content']}"
  return result


class DevAgent(Page):
  class ResultSignal(QObject):
    signal = Signal(str)

  def __init__(self):
    super().__init__('agent')
    self.template = template
    self.style = style
    self.update_signal = self.ResultSignal()
    self.update_signal.signal.connect(self.update_content)
    
    def log(*args):
      print(' '.join(args))
      self.update_signal.signal.emit(' '.join(args))

    def call_api(messages):
      self.pageParam.set('reply', '')
      send_to_ai = convert_messages(messages)
      log(send_to_ai)
      resp = call_qwen(messages, api_key=getSetting('QWEN_API_KEY'))
      log(f"{BLOCK_LINE}🤖assistant: " + resp)
      return resp
    self.agent = DevAgentPlugin(call_api, mcp_dict, max_steps=5, has_tail=False)

  def setup(self):
    return {
      'title': 'AI智能体',
      'reply': encode(self.pageParam.get('reply', '')),
    }

  def show(self, *args):
    self.register('message', 'returnPressed', self.submit)
    self.register('submit', 'clicked', self.submit)

  def submit(self, *args):
    submitBtnText = self.getWidget('submit').text()
    if submitBtnText != '发送':
      self.tips('AI正在回答，请稍等', 'fail')
      return

    message = self.getWidget('message').text()
    if not message.strip():
      self.tips('请输入要发送的内容', 'fail')
      return
    self.pageParam.set('message', message)
    self.pageParam.set('start_time', time.time())

    self.getWidget('message').setText('')
    self.getWidget('submit').setText('稍等')
    self.setClass('shell', 'shell running')
    self.async_run(self.devmate_ask, self.devmate_response)

  def devmate_ask(self):
    return self.agent.chat(self.pageParam.get('message', ''))

  def devmate_response(self, reply):
    self.setClass('shell', 'shell')
    self.getWidget('submit').setText('发送')
    start_time = self.pageParam.get('start_time', 0)
    end_time = time.time()
    cost_time = round(end_time - start_time, 2)
    result = f"{BLOCK_LINE}✅任务结束(耗时{cost_time}秒)"
    self.update_content(result)
    self.playMedia('media', 'task_done_ai.mp3')

  def update_content(self, text):
    reply = self.pageParam.get('reply', '') + text
    reply_widget = self.getWidget('shell')
    reply_widget.setPlainText(reply)
    vertical_scroll_bar = reply_widget.verticalScrollBar()
    vertical_scroll_bar.setValue(vertical_scroll_bar.maximum())
    self.pageParam.set('reply', reply)