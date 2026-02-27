import time
from PySide6.QtCore import QObject, Signal
from app_page import Page
from app_page.utils import encode, call_qwen
from app_page.plugins import DevAgent

API_KEY = "sk-**************************"

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
  "system_info": {
    "url": "http://127.0.0.1:8080/system_info",
    "param": [],
    "description": "获取系统信息，如处理器型号、内存大小、硬盘使用情况等"
  },
}

def convert_messages(messages):
  result = ""
  for item in messages:
    if item['role'] == 'system':
      result += f"💻system: {item['content']}"
    elif item['role'] == 'user':
      result += f"\r\n\r\n👨user: {item['content']}"
    else:
      result += f"\r\n\r\n🤖assistant: {item['content']}"
  return result


class Agent(Page):
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
      resp = call_qwen(messages, api_key=API_KEY)
      log("\r\n\r\n🤖assistant: " + resp)
      return resp
    self.agent = DevAgent(call_api, mcp_dict, max_steps=5)

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
    self.async_run(self.devmate_ask, self.devmate_response)

  def devmate_ask(self):
    return self.agent.chat(self.pageParam.get('message', ''))

  def devmate_response(self, reply):
    self.getWidget('submit').setText('发送')
    start_time = self.pageParam.get('start_time', 0)
    end_time = time.time()
    cost_time = round(end_time - start_time, 2)
    result = f"\r\n\r\n✅任务结束(耗时{cost_time}秒)"
    self.update_content(result)

  def update_content(self, text):
    reply = self.pageParam.get('reply', '') + text
    reply_widget = self.getWidget('shell')
    reply_widget.setPlainText(reply)
    vertical_scroll_bar = reply_widget.verticalScrollBar()
    vertical_scroll_bar.setValue(vertical_scroll_bar.maximum())
    self.pageParam.set('reply', reply)