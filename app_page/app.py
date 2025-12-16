import sys
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app_page_core import Store, Param
from .core import ThreadManager, PageManager, Page, Device, Setting
from .components import StackManager
from .MainWindow import MainWindow
from .config import Config
from .utils import assetsPath


def createApp(SETTING: dict):
  """创建应用
  Args:
    SETTING (dict): 设置字典, 参数如下
    stack_id (str): 栈组件id
    pages (dict): 页面字典
    pageOptionList (list): 页面配置项列表
    button_container_id (str): 按钮容器id
    button_close_id (str): 关闭按钮id
    button_login_id (str): 登录按钮id
    button_name_id (str): 按钮名称id
    Ui_MainWindow (Ui_MainWindow): 主窗口ui对象
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
  if 'IS_DEBUG' in SETTING:
    Setting.applySetting('IS_DEBUG', SETTING['IS_DEBUG'])
  config = Config()
  default_settings = {
    'stack_id': 'stackedWidget',
    'pages': config.pages,
    'pageOptionList': config.pageOptionList,
    'button_container_id': config.button_container_id,
    'button_close_id': config.button_close_id,
    'button_login_id': config.button_login_id,
    'button_name_id': config.button_name_id,
    'APP_ICON_PATH': config.APP_ICON_PATH,
    'APP_TITLE': config.APP_TITLE,
    'APP_VERSION': config.APP_VERSION,
    'IS_DEBUG': config.IS_DEBUG,
    'PING_HOST': config.PING_HOST,
    'tips_ui': config.tips_ui,
    'tipsBox_ui': config.tipsBox_ui,
    'loading_icon': config.loading_icon,
    'small_page_icon': config.small_page_icon,
    'maximize_page_icon': config.maximize_page_icon,
  }
  final_settings = {**default_settings, **SETTING}
  Setting.applySetting(final_settings)
  
  if 'beforeCreate' in SETTING and callable(SETTING['beforeCreate']):
    SETTING['beforeCreate']()
  
  app = QApplication(sys.argv)
  app.setWindowIcon(QIcon(Setting.getSetting('APP_ICON_PATH')))

  defaultValue = Device.defaultSystemConfig(version=Setting.getSetting('APP_VERSION'))
  filePath = Param(filePath=None, default=defaultValue).pathJoin("systemPath", "param.json")
  param = Param(filePath=filePath, default=defaultValue)
  param.set('systemPath', defaultValue.get('systemPath', ''))
  param.set('tempPath', defaultValue.get('tempPath', ''))
  param.set('userPath', defaultValue.get('userPath', ''))
  playMedia = initPlayer(app)
  store = Store({
    'app': app,
    'param': param,
    'playMedia': playMedia,
  })

  mainWin = MainWindow(param)
  threadManager = ThreadManager()
  pageManager = PageManager()
  root = Page('root')

  def closeApp(beforeClose: callable = None):
    if beforeClose and callable(beforeClose):
      beforeClose()
    
    param.save()
    pageManager.destroy()
    threadManager.remove()
    root.children.remove()

    app.quit()
  
  store.set('root', root)
  store.set('closeApp', closeApp)
  store.set('mainWin', mainWin)
  store.set('threadManager', threadManager)
  store.set('pageManager', pageManager)
  
  stackManager = initStackManager(root, mainWin)
  store.set('stackManager', stackManager)
  
  mainWin.callback.add('close', lambda: root.closeApp())
  root.closeApp = closeApp
  
  mainWin.setUserInfo('请登录', '')
  mainWin.setAppStyle()
  
  initMainWinRegister(root, mainWin, stackManager)
  root.setup()
  mainWin.show()
  
  if 'onMounted' in SETTING and callable(SETTING['onMounted']):
    SETTING['onMounted'](root)
  
  exit_code = app.exec()
  sys.exit(exit_code)


def initPlayer(target):
  """初始化 QMediaPlayer 并返回播放函数"""
  audioOutput = QAudioOutput()
  audioOutput.setVolume(50)
  player = QMediaPlayer()
  player.setAudioOutput(audioOutput)

  def playMedia(*args):
    """播放多媒体文件 (路径通过 assetsPath 计算)
    
    Args:
        args (tuple): 目录，文件名
    """
    player.setSource(QUrl.fromLocalFile(assetsPath(*args)))
    player.play()
  
  target.__player = player
  target.__audioOutput = audioOutput
  return playMedia


def initMainWinRegister(root: Page, mainWin: MainWindow, stackManager: StackManager):
  """注册主窗口右上角的按钮事件"""
  rightTopBinds: dict = Setting.getSetting('rightTopBinds', {})

  # 辅助函数：导航到页面并清除按钮样式
  def navigate_and_clear(page_id: str):
    root.navigateTo(page_id)
    stackManager.clearActiveStyle()
  
  # 登录/用户事件：从配置中获取，或使用默认提示
  loginEvent = rightTopBinds.get(
    'btn_login_icon', 
    lambda: root.tips('点击了登录图标，可通过 rightTopBinds 更改绑定事件', 'success')
  )
  
  # 注册事件
  mainWin.register('btn_login_icon', 'clicked', loginEvent)
  mainWin.register('btn_login_text', 'clicked', loginEvent)
  mainWin.register('btn_setting', 'clicked', lambda: navigate_and_clear('setting'))
  mainWin.register('btn_message', 'clicked', lambda: navigate_and_clear('message'))
  mainWin.register('btn_skin', 'clicked', lambda: navigate_and_clear('skin'))


def initStackManager(root: Page, mainWin: MainWindow):
  """初始化页面管理器和堆栈管理器"""
  stack_id: str = Setting.getSetting('stack_id')
  button_frame_id: str = Setting.getSetting('button_frame_id')
  button_container_id: str = Setting.getSetting('button_container_id')
  pages: dict = Setting.getSetting('pages')
  pageOptionList: list = Setting.getSetting('pageOptionList')
  
  # 挂载到页面管理器
  root.pageManager.mount(mainWin.getWidget(stack_id), pages=pages, pageOptionList=pageOptionList)
  
  # 创建导航 (StackManager)
  stackManager = StackManager({
    "stack_id": stack_id,
    "pageOptionList": pageOptionList,
    "button_frame_id": button_frame_id,
    "button_container_id": button_container_id,
  })
  stackManager.setup()
  return stackManager