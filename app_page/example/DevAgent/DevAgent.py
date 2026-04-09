import time
from PySide6.QtCore import QObject, Signal
from app_page import Page, getSetting
from app_page.utils import encode, call_qwen, assetsUrl, updateStyle
from app_page.plugins import DevAgent as DevAgentPlugin
from .DevAgentSetting import setting, setting_close
from .mcp_dict import mcp_dict

template = """
<template>
  <div id="main-ui" class="container" margins="[10, 10, 10, 10]">
    <v-box spacing="10" margins="[0,0,0,0]">
      <div>
        <h-box margins="[0,0,0,0]">
          <label text="${title}" class="title"/>
          <button id="setting" class="text-button" text="设置" width="60" height="26" />
        </h-box>
      </div>
      <div>
        <h-box margins="[0,0,0,0]" >
          <line-edit id="message" text="" style="border-radius:6px;" placeholder="告诉智能体你想要做的事情..." />
          <button id="submit" width="24" height="24" class="submit" />
        </h-box>
      </div>
      <text-edit id="shell" class="shell" text="${reply}" />
    </v-box>
  </div>
</template>
"""

create_style = lambda: """
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
.shell.running {
  background-color: #ACC7F6;
}
.text-button {
  font-size: 14px;
  border-radius: 6px;
  color: #fff;
  background-color: #409EFF;
}
.submit {
  background-image: url(""" + assetsUrl('icon', 'send.png') + """);
}
.loading {
  background-image: url(""" + assetsUrl('icon', 'loading.png') + """);
}
"""
BLOCK_LINE = '\r\n\r\n'
SYSTEM_PROMPT = '''
### 调用规则
1. 你需要根据用户输入判断是否调用工具，如果需要，按照上述调用格式输出指令即可，不需回复多余文字。
2. 工具调用除store_text外，必须以按照以下格式，"[TOOL] <tool_name> <JSON_PARAMS> [TOOL END]"，其中<JSON_PARAMS>必须是合法JSON字符串。
3. 工具调用store_text，只需返回"[TOOL STORE TEXT START]"和"[TOOL STORE TEXT END]"标签包裹内容的指令即可。
4. 若工具调用错误后续不再继续调用，提醒用户失败原因。
5. 若工具调用成功认真判断后续操作，避免反复调用工具。
6. 调用工具返回的结果用户能看见你无需复述，只需要给出你觉得必要的回答。
7. 每次只能调用一个工具，如果不需要调用工具，请直接给出简洁、专业、像开发助理的回答。

### 建议的操作
1. 建议写入文本之前先使用store_text工具，并使用提取码来作为content写入文件。
2. 建议认真判断工具返回的结果，分析用户的核心问题是否解决，以确定下一步是继续调用工具还是给用户最终回复。
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
    self.style = create_style()
    self.update_signal = self.ResultSignal()
    self.update_signal.signal.connect(self.update_content)
    self.agent = None
    self.load()

  def load(self):
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
    
    user_mcp_dict = self.localStore.get('setting/mcp_dict', mcp_dict)
    project_path = self.localStore.get('setting/project_path', '')
    new_system_prompt = SYSTEM_PROMPT + '\r\n' + f'当前项目路径: {project_path}\r\n'
    self.agent = DevAgentPlugin(call_api, user_mcp_dict, max_steps=5, system_prompt=new_system_prompt)

  def setup(self):
    return {
      'title': 'AI智能体',
      'reply': encode(self.pageParam.get('reply', '')),
    }

  def show(self, *args):
    self.register('setting', 'clicked', lambda: setting(self, self.load))
    self.register('message', 'returnPressed', self.submit)
    self.register('submit', 'clicked', self.submit)

  def hide(self, *args):
    setting_close()

  def submit(self, *args):
    if self.pageParam.get('loading', False):
      self.tips('AI正在回答，请稍等', 'fail')
      return

    message = self.getWidget('message').text()
    if not message.strip():
      self.tips('请输入要发送的内容', 'fail')
      return
    
    self.pageParam.set('loading', True)
    self.pageParam.set('message', message)
    self.pageParam.set('start_time', time.time())

    self.setText('message', '')
    self.setClass('submit', 'loading')
    self.setClass('shell', 'shell running')
    updateStyle(self.getWidget('main-ui'))
    self.async_run(self.devmate_ask, self.devmate_response)

  def devmate_ask(self):
    return self.agent.chat(self.pageParam.get('message', ''))

  def devmate_response(self, reply):
    self.setClass('submit', 'submit')
    self.setClass('shell', 'shell')
    updateStyle(self.getWidget('main-ui'))
    self.pageParam.set('loading', False)
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