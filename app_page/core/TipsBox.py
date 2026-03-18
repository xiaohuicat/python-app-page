from typing import Optional, Callable
from ..core.CallPanel import CallPanel
from ..utils import encode

main_template = '''
<div id="main_container" width="270" height="335" size_policy="True">
  <v-box margins="[0, 0, 0, 0]" align="AlignCenter" spacing="20">
    <label class="title" text="${title}" />
    <label class="content" text="${content}" />
    <div>
      <h-box margins="[0, 20, 0, 0]" spacing="20">
        <button id="cancel" class="light-button" height="40" text="取消" />
        <button id="submit" class="dark-button" height="40" text="确认" />
      </h-box>
    </div>
  </v-box>
</div>
'''

main_style = '''
.title {
  color: #333;
  font-size: 20px;
  font-weight: bold;
}
.content {
  color: #888;
  font-size: 14px;
}
.light-button {
  padding: 0 10px;
  color: #000;
  background-color: #fff;
  border-radius: 12px;
  font-size: 16px;
  border: 1px solid #000;
}

.dark-button {
  padding: 0 10px;
  color: #fff;
  background-color: #000;
  border-radius: 12px;
  font-size: 16px;
}
'''

store = {}


def tipsBox(
    topic:str="更新提醒", 
    title:str="提示窗的标题", 
    content:str="提示的内容",
    confirm: Optional[Callable] = None,
    cancel: Optional[Callable] = None,
    close: Optional[Callable] = None) -> None:
    """
    显示弹窗
      :param topic: 提示框主题
      :param title: 提示框标题
      :param content: 提示框内容
      :param confirm: 确认按钮回调
      :param cancel: 取消按钮回调
      :param close: 关闭按钮回调
    """
    main_params = {
      'title': encode(title),
      'content': encode(content),
    }
    options = {
      "id": "tips_box_position",
      "width": 300,
      "height": 400,
      "title": ' ',
      "radius": 14,
      "topic": topic,
    }
    close_panel()
    panel = CallPanel(main_template, main_params, main_style, options)
    panel.callback.add('before_close', close)
    panel.showPanel()

    def handle_confirm():
        if callable(confirm):
            confirm()
        close_panel()

    def handle_cancel():
        if callable(cancel):
            cancel()
        close_panel()
    
    panel.register('submit', 'clicked', handle_confirm)
    panel.register('cancel', 'clicked', handle_cancel)
    store['store_panel'] = panel


def close_panel():
  if 'store_panel' in store:
    store['store_panel'].destroy()
    del store['store_panel']