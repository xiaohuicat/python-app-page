import os,sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app_page_core import Store, Param
from .core import ThreadManager, PageManager, Page, Device, Setting, MainWindow
from .components import StackManager
from .config import *
from .utils import setAppStyle, assetsPath
from .example import Skin
from .apprcc_rc import *

# 绑定顶部右侧按钮
class BindsRightTop(Page):
  def binds(self):
    return {
      "clicked": [
        ("btn_skin", lambda :self.tips('点击了皮肤', 'success')),
        ("btn_login_icon", lambda :self.tips('点击了登录图标', 'success')),
        ("btn_login_text", lambda :self.tips('点击了登录名称', 'success')),
        ("btn_setting", lambda :self.tips('点击了设置', 'success')),
        ("btn_message", lambda :self.tips('点击了消息', 'success')),
      ]
    }

# 需要加载的页面
pages = {
  "chat": Page,
  "setting": Page,
  "skin": Skin,
  "message": Page,
}

# 页面配置项列表
pageOptionList = [
  {
    "name": "测试页面1",
    "id": "chat",
    "filter": "leftBar",
    "icon": "assets/icon/leftbar/chat.png",
    "stack_id": "app_page_chat",
    "right_menu":[
      {"name": "移除", "icon": assetsPath('menu', 'remove.png')},
      {"name": "设置", "icon": assetsPath('menu', 'setting.png')}
    ]
  },
  {
    "name": "测试页面2",
    "id": "setting",
    "filter": "leftBar",
    "icon": "assets/icon/right_top_bar/setting.png",
    "stack_id": "app_page_setting"
  },
  {
    "name": "主题",
    "id": "skin",
    "filter": "right_top_bar",
    "icon": "assets/icon/right_top_bar/skin.png",
    "stack_id": "app_page_skin"
  },
  {
    "name": "信息",
    "id": "message",
    "filter": "right_top_bar",
    "icon": "assets/icon/right_top_bar/message.png",
    "stack_id": "app_page_message"
  }
]

def loadStackPages(target:Page):
  """加载页面

  Args:
      target (Page): 页面对象
  """
  stack_id:str = Setting.getSetting('stack_id')
  filter_id:str = Setting.getSetting('filter_id')
  button_frame_id:str = Setting.getSetting('button_frame_id')
  button_container_id:str = Setting.getSetting('button_container_id')
  pages:dict = Setting.getSetting('pages')
  pageOptionList:list = Setting.getSetting('pageOptionList')
  
  # 挂载到页面管理器
  target.pageManager.mount(target.ui[stack_id], pages=pages, pageOptionList=pageOptionList)
  # 创建导航
  stackManager = StackManager({
    "stack_id": stack_id,
    "filter_id": filter_id,
    "pageOptionList": pageOptionList,
    "button_frame_id": button_frame_id,
    "button_container_id": button_container_id,
  })
  stackManager.initPage()
  bindsRightTop = BindsRightTop()
  bindsRightTop.initPage()
  target.children.add("bindsRightTop", bindsRightTop)
  target.children.add("stackManager", stackManager)

def createApp(SETTING:dict):
  """创建应用
  Args:
      SETTING (dict): 设置字典, 参数如下>>>
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
  # 应用默认配置
  Setting.applySetting({
    'stack_id': 'stackedWidget',
    'pages': pages,
    'pageOptionList': pageOptionList,
    'filter_id': filter_id,
    'button_frame_id': button_frame_id,
    'button_container_id': button_container_id,
    'button_close_id': button_close_id,
    'button_login_id': button_login_id,
    'button_name_id': button_name_id,
    'APP_ICON_PATH': APP_ICON_PATH,
    'APP_TITLE': APP_TITLE,
    'APP_VERSION': APP_VERSION,
    'IS_DEBUG': IS_DEBUG,
    'PING_HOST': PING_HOST,
    'tips_ui': tips_ui,
    'tipsBox_ui': tipsBox_ui,
    'loading_icon': loading_icon,
    'small_page_icon': small_page_icon,
    'maximize_page_icon': maximize_page_icon,
  })
  # 应用用户配置
  Setting.applySetting(SETTING)
  # 创建应用，添加图标
  app = QApplication(sys.argv)
  app.setWindowIcon(QIcon(APP_ICON_PATH))  # 生成exe时改为绝对路径
  # 创建全局参数对象
  param = Param(filePath=None, default=Device.defaultSystemConfig(version=APP_VERSION))
  user_param = Param(os.path.join(param.get("userPath", ""), "user.json"), {})
  system_param = Param(os.path.join(param.get("systemPath", ""), "system.json"), {})
  # 创建程序主窗口
  main_win = MainWindow(system_param)
  threadManager = ThreadManager()
  pageManager = PageManager()
  # 创建全局变量
  Store({
    'app': app,
    'main_win': main_win,
    'ui': main_win.ui,
    'threadManager': threadManager,
    'pageManager': pageManager,
    'param': param,
    'user_param': user_param,
    'system_param': system_param,
  })
  root = Page('root')
  avatar_url = param.pathJoin("userPath", 'images/avatar.png')
  main_win.ui[Setting.getSetting('button_close_id')].clicked.connect(lambda: root.closeApp())
  main_win.ui[Setting.getSetting('button_login_id')].setStyleSheet(f'image: url({avatar_url})')
  main_win.ui[Setting.getSetting('button_name_id')].setText(user_param.get('userInfo/name', "未命名")[:3])
  # 设置样式，必须在创建全局变量之后
  setAppStyle(root)
  # 挂载栈页面
  loadStackPages(root)
  # 根页面初始化
  root.setup()
  # 显示窗口
  main_win.show()
  print(f"----APP_TITLE:{APP_TITLE} APP_VERSION:{APP_VERSION}----")
  # 运行APP
  n = app.exec()
  try:
      sys.exit(n)
  except SystemExit:
      sys.exit(n)
