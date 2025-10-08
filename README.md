# PySide6 app framework

# 安装库
```shell
pip install app-page
```
# 模块说明
- core        程序核心模块
- animation   动画模块
- plugins     插件模块
- utils       工具模块

# 使用案例
```python
from app_page import Page, createApp

# 模版支持moka语法，接受setup返回词典中的变量
template = """
<template>
  <div style="color:#333;background-color:#fff;border-radius:10px;" height="250">
    <v-box>
      <label text="${title}" style="font-size:20px;color:#333;" />
      <text-edit id="editor" style="background-color:#e0e0e0;border-radius:10px;padding:10px;font-size:16px;" />
      <button id="help" text="${button_text}" height="32" width="100" style="background-color:#000;color:#fff;border-radius:10px;" />
    </v-box>
  </div>
</template>
"""

# 编辑页面
class Editor(Page):
  def __init__(self):
    # 初始化添加名称自动生成持久化对象，可通过self.localStore访问
    super().__init__("editor")
    self.template = template

  def setup() -> dict:
    # 此处返回的变量可在moka模版中使用
    return {
      'title': '写点东西吧(自动保存)',
      'button_text': '使用说明',
    }

  def show(self, *args):
    # 获取持久化编辑内容
    content = self.localStore.get("editor-value", '')
    # 根据id获取标签渲染组件并设置内容
    self.getWidget("editor").setPlainText(content)
    # 注册事件，(id，事件类型，回调函数)
    self.register("editor", 'textChanged', lambda *args: self.textChange())
    self.register("help", 'clicked', lambda *args: self.tips('没别的说明了，自己摸索一下', 'success'))

  # 值改变更新到持久化内容
  def textChange(self):
    self.localStore.set("editor-value", self.getWidget("editor").toPlainText())

# 设置页面
class Setting(Page):
  def __init__(self):
    super().__init__()
    self.template = """
<template>
  <div style="color:#333;background-color:#fff;border-radius:10px;">
    <v-box>
      <label text="系统设置" style="font-size:20px;color:#333;" />
    </v-box>
  </div>
</template>
"""

# 创建应用
createApp(SETTING={
  "APP_TITLE": "桌面软件",
  "IS_DEBUG": True, # 调试模式，面板打印更多调试数据
  "pages": {
    "editor": Editor, 
    "setting": Setting,
  },
  "pageOptionList": [
    {
      "name": "随心笔记",
      "id": "editor",
      "filter": "leftBar",
      "stack_id": "app_page_editor",
    },
    {
      "name": "系统设置",
      "id": "setting",
      "filter": "leftBar",
      "stack_id": "app_page_setting",
    }
  ],
})
```
# 运行结果
<img src="./assets/example.png" alt="app-page" />