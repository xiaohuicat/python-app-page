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
  "store_text": {
    "url": "http://127.0.0.1:8080/store_text",
    "description": "存储文本内容，参数text是要存储的文本字符串，调用成功后会返回一个8位提取码，其它工具若支持可以直接输入提取码来获取文本内容。适用于需要存储较长文本内容的场景，避免直接在工具调用中传输过长文本导致解析困难。",
    "usage": "[TOOL STORE TEXT START]和[TOOL STORE TEXT END]标签包裹的文本就是要存储的内容",
  },
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
    "description": "写入内容到本地文件。file_path是文件路径；content是要写入的字符串内容，支持直接输入提取码"
  },
  "delete_file": {
    "url": "http://127.0.0.1:8080/delete_file",
    "param": ["file_path"],
    "description": "删除本地文件，file_path是文件路径"
  },
  "download_file": {
    "url": "http://127.0.0.1:8080/download_file",
    "param": ["url", "save_path"],
    "description": "下载文件到本地，url是文件链接，save_path是要保存的本地路径"
  },
  "search_files": {
    "url": "http://127.0.0.1:8080/search_files",
    "param": ["pattern", "path", "max_results"],
    "description": "按模式搜索文件，pattern是搜索模式，path是搜索路径（默认当前目录），max_results是最大返回结果数（默认100）"
  },
  "system_info": {
    "url": "http://127.0.0.1:8080/system_info",
    "param": [],
    "description": "获取系统信息，如CPU、内存、磁盘、处理器型号、内存大小、硬盘使用情况等"
  },
  "list_processes": {
    "url": "http://127.0.0.1:8080/list_processes",
    "param": [],
    "description": "列出所有运行中的进程信息"
  },
  "kill_process": {
    "url": "http://127.0.0.1:8080/kill_process",
    "param": ["pid", "force"],
    "description": "终止指定PID的进程，pid是进程ID，force是否强制杀死（默认false）"
  },
  "run_shell_command": {
    "url": "http://127.0.0.1:8080/run_shell_command",
    "param": ["command", "timeout", "cwd"],
    "description": "执行Shell命令，command是要执行的命令，timeout超时时间（默认30秒），cwd工作目录"
  },
  "network_info": {
    "url": "http://127.0.0.1:8080/network_info",
    "param": [],
    "description": "获取网络接口、路由、端口等网络信息"
  },
  "view_logs": {
    "url": "http://127.0.0.1:8080/view_logs",
    "param": ["log_path", "lines"],
    "description": "查看日志文件内容，log_path是日志文件路径，lines是读取行数（默认100）"
  },
  "get_weather": {
    "url": "http://127.0.0.1:8080/get_weather",
    "param": ["citycode"],
    "description": "获取指定城市的天气信息，citycode是城市编码，北京是110101"
  },
  "draw_image": {
    "url": "http://127.0.0.1:8080/draw_image",
    "param": ["prompt", "size"],
    "description": "根据提示词生成图像，prompt是提示词，size是图像大小（支持1328*1328）"
  },
}

BLOCK_LINE = '\r\n\r\n'
SYSTEM_PROMPT = '''
调用规则：
1. 你需要根据用户输入判断是否调用工具，调用哪个工具；如果需要，必须严格按照上述“调用格式”输出，不要加任何多余文字
2. 工具调用除store_text外，必须以按照以下格式，"[TOOL] <tool_name> <JSON_PARAMS> [TOOL END]"，如"[TOOL] read_file {{"path":"/Users/my_project/readme.md"}} [TOOL END]"。
3. 工具调用store_text，必须以"[TOOL STORE TEXT START]"和"[TOOL STORE TEXT END]"标签包裹要存储的文本内容，如"[TOOL STORE TEXT START]这是要存储的文本内容[TOOL STORE TEXT END]"。
4. 调用工具的参数为路径时必须是绝对路径。
5. 如果不需要调用工具，请直接给出简洁、专业、像开发助理的回答。
6. 若工具调用错误后续不再继续调用，提醒用户失败原因。
7. 若工具调用成功认真判断后续操作，避免反复调用工具。
8. 你每次只能调用一个工具，请勿调用多个。
9. 调用工具返回的结果用户能看见你无需复述，只需要给出你觉得必要的回答。

写入文本之前建议先使用store_text工具，并使用提取码来获取文本内容， 这样不容易出现错误，并且节约token。
'''

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
    self.agent = DevAgentPlugin(call_api, mcp_dict, max_steps=5, has_tail=False, system_prompt=SYSTEM_PROMPT)

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