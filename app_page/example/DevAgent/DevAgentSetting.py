from app_page import Page, WidgetsController, render
from app_page.utils import assetsPath, encode, get_valid_json, format_json
from app_page.components.CallPanel import CallPanel
from .mcp_dict import mcp_dict

template_setting = '''
<template>
  <div id="main_container">
    <v-box margins="[0, 0, 0, 0]" align="AlignTop">
      <div>
        <v-box margins="[0, 10, 0, 0]" spacing="16">
          <label text="当前项目地址" />
          <line-edit id="project-path" text="${projectPath}" placeholder="输入当前项目地址" height="40" class="line-input" />
        </v-box>
      </div>

      <div>
        <v-box margins="[0, 10, 0, 0]" spacing="16">
          <label text="MCP配置词典" />
          <text-edit id="mcp-dict" text="${mcpDict}" placeholder="输入MCP配置词典" height="250" class="text-input" />
        </v-box>
      </div>

      <div>
        <v-box margins="[0, 20, 0, 0]" spacing="20">
          <button id="resume" class="light-button" height="40" text="还原" />
          <button id="submit" class="dark-button" height="40" text="确认" />
        </v-box>
      </div>
    </v-box>
  </div>
</template>
'''

template_style = '''
.line-input {
  padding: 0 10px;
  color: #444;
  background-color: #fff;
  border-radius: 12px;
  font-size: 14px;
  border: 1px solid #ccc;
}

.text-input {
  padding: 5px;
  color: #444;
  background-color: #fff;
  border-radius: 12px;
  font-size: 14px;
  border: 1px solid #ccc;
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

def setting(page:Page, onSettingDone):
    title = "Agent设置"
    config = {
      "id": "agent-setting-pop",
      "size_w_h": [500, 600],
      "transparent": True,
      "pin_to_top": True,
      "movable": True,
      "shadow_effect": True,
      "title": f"    {title}",
      "main_layout": "V",
      "style": {
        "background-color": '#fff',
        "border-radius": '10px',
      }
    }
    setting_close()
    panel = CallPanel(page.param, config)
    panel.show()
    panel.callback.add('before_close', setting_close)
    user_mcp_dict = page.localStore.get('setting/mcp_dict', mcp_dict)
    project_path = page.localStore.get('setting/project_path', '')
    render_dict = render(panel.layout_main, template_setting, {
      'mcpDict': encode(format_json(user_mcp_dict)),
      'projectPath': encode(project_path),
    })
    wc = WidgetsController(render_dict['widget_id_map'], render_dict['widget_list'])

    with open(assetsPath('UI', 'style.qss'), 'r', encoding='utf-8') as file:
      commonStyle = file.read()
      wc.getWidget('main_container').setStyleSheet(commonStyle + template_style)

    def submit():
      projectPath = wc.getWidget('project-path').text()
      input_mcp_dict = wc.getWidget('mcp-dict').toPlainText()
      try:
        valid_mcp_dict = get_valid_json(input_mcp_dict)
      except Exception as e:
        page.tips(f'JSON格式错误: {str(e)}', 'fail')
        return
      
      page.localStore.set('setting/project_path', projectPath)
      page.localStore.set('setting/mcp_dict', valid_mcp_dict)
      page.tips('设置成功', 'success')
      if callable(onSettingDone):
        page.setTimeout(lambda *args:onSettingDone(), 0.1)
      setting_close()

    def resume():
      def confirm():
        page.localStore.set('setting/mcp_dict', mcp_dict)
        page.localStore.set('setting/project_path', '')
        page.tips('还原成功', 'success')
        if callable(onSettingDone):
          page.setTimeout(lambda *args:onSettingDone(), 0.1)
        setting_close()
      page.tipsBox('确认弹窗', '是否确认还原数据', '用户配置将丢失是否还原？', confirm)

    wc.register('submit', 'clicked', submit)
    wc.register('resume', 'clicked', resume)
    panel._wc = wc
    store['setting_callpanel'] = panel


def setting_close():
  if 'setting_callpanel' in store:
    panel = store["setting_callpanel"]
    panel.close()
    if hasattr(panel, '_wc'):
      panel._wc.destroy()
      delattr(panel, '_wc')
    del store["setting_callpanel"]