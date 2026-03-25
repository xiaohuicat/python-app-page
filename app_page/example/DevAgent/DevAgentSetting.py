from app_page import Page, CallPanel, PanelStore
from app_page.utils import encode, get_valid_json, format_json
from .mcp_dict import mcp_dict

main_template = '''
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
'''

main_style = '''
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

ps = PanelStore()

setting_close = lambda: ps.close()

def setting(page:Page, on_setting_done):
    title = "Agent设置"
    options = {
      "id": "agent-setting-pop",
      "height": 575,
      "title": f"    {title}",
    }
    user_mcp_dict = page.localStore.get('setting/mcp_dict', mcp_dict)
    project_path = page.localStore.get('setting/project_path', '')
    main_params = {
      'mcpDict': encode(format_json(user_mcp_dict)),
      'projectPath': encode(project_path),
    }
    panel = CallPanel(
      main_template=main_template, 
      main_params=main_params, 
      style_sheet=main_style, 
      options=options
    )

    def submit():
      projectPath = panel.getWidget('project-path').text()
      input_mcp_dict = panel.getWidget('mcp-dict').toPlainText()
      try:
        valid_mcp_dict = get_valid_json(input_mcp_dict)
      except Exception as e:
        page.tips(str(e), 'fail')
        return
      
      page.localStore.set('setting/project_path', projectPath)
      page.localStore.set('setting/mcp_dict', valid_mcp_dict)
      page.tips('设置成功', 'success')
      if callable(on_setting_done):
        page.setTimeout(lambda *args:on_setting_done(), 0.1)
      ps.close()

    def resume():
      def confirm():
        page.localStore.set('setting/mcp_dict', mcp_dict)
        page.localStore.set('setting/project_path', '')
        page.tips('还原成功', 'success')
        if callable(on_setting_done):
          page.setTimeout(lambda *args:on_setting_done(), 0.1)
        ps.close()
      page.tipsBox('确认弹窗', '是否确认还原数据', '用户配置将丢失是否还原？', confirm)

    panel.register('submit', 'clicked', submit)
    panel.register('resume', 'clicked', resume)
    
    ps.add(panel)
    panel.showPanel()