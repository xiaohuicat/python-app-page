# PySide6 app framework

# Installation
```shell
pip install app-page
```
# 模块说明
- core        程序核心模块
- animation   动画模块
- plugins     插件模块
- utils       工具模块

# Usage
使用案例
```python
from app_page import Page, createApp

"""
SETTINGS (dict): 设置参数
    stack_id (str): 栈组件id
    pages (dict): 页面字典
    pageOptionList (list): 页面配置项列表
    filter_id (str): 过滤器id，用来筛选当前显示的页面
    button_frame_id (str): 按钮框架id
    button_container_id (str): 按钮容器id
    button_close_id (str): 关闭按钮id
    button_login_id (str): 登录按钮id
    button_name_id (str): 按钮名称id
    APP_ICON_PATH (str): 应用图标路径
    APP_TITLE (str): 应用标题
    APP_VERSION (str): 应用版本
    IS_DEBUG (bool): 是否调试模式
    PING_HOST (str): 网络连接检查地址
    tips_ui (str|Ui_Form): 提示提示消息ui路径或Ui_Form类
    tipsBox_ui (str|Ui_Form): 提示提示框ui路径或Ui_Form类
    loading_icon (str): 加载图标路径
    small_page_icon (str): 缩小图标路径
    maximize_page_icon (str): 最大窗口图标路径
"""
createApp(SETTINGS)
```