import os,sys
import apprcc_rc
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app_page_core import Store, Param, PageManager
from .core import ThreadManager, Page, Device, Setting, MainWindow
from .config import APP_ICON_PATH, APP_VERSION, APP_TITLE, PING_HOST, IS_DEBUG, tips_ui, tipsBox_ui, loading_icon, small_page_icon, maximize_page_icon
from .utils import setAppStyle

def createApp(SETTING:dict):
  Setting.applySetting({
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

  Root = Setting.getSetting('Root', None)
  if not Root:
    raise Exception("Root is None")
  root:Page = Root()
  root.setup()
  
  # 绑定关闭事件
  main_win.ui.btn_close.clicked.connect(lambda: root.closeApp())

  # 设置样式，必须在创建全局变量之后
  setAppStyle(root)

  n = app.exec()
  try:
      sys.exit(n)
  except SystemExit:
      sys.exit(n)