# PySide6 app framework

# Installation
```shell
pip install app-page
```
# 模块说明
- core        程序核心模块
- animation   动画模块
- plugins     插件模块

# Usage
使用案例
```python
from app_page import Page, createApp

# 根页面，运行createApp函数初始化完成后进行根页面的初始化。
class Root(Page):
    def setup(self):
        super().setup()
        # 显示主窗口
        self.store.get('main_win').show()

createApp({
    "Root": Root,
})
```