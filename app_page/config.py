import os, shutil
from .core import Setting

def assetsPath(*args):
    """获取资源路径
    Args:
        args (tuple): 目录，文件名

    Returns:
        path (str): 资源绝对路径
    """
    is_debug = Setting.getSetting("IS_DEBUG", False)
    packagePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", *args)
    appPath = os.path.join(os.getcwd(), "assets", *args)
    if not is_debug:
      # 确保目标目录的父目录存在
      os.makedirs(os.path.dirname(appPath), exist_ok=True)
      # 检查源路径是否存在
      if os.path.exists(packagePath):
        try:
          # 复制文件或目录
          if os.path.isfile(packagePath):
            shutil.copy(packagePath, appPath)
          else:
            shutil.copytree(packagePath, appPath, dirs_exist_ok=True)
        except Exception as e:
          raise SystemError("复制文件或目录时出错", e)
      else:
        print("源路径不存在:", packagePath)
      return appPath
    else:
      return packagePath

class Config():
  def __init__(self):
    self.tips_ui = assetsPath("tips.ui")
    self.tipsBox_ui = assetsPath("tipsBox.ui")
    self.MainWindow_ui = assetsPath("main.ui")
    self.loading_icon = assetsPath("loading.gif")
    self.small_page_icon = assetsPath("small_page.png")
    self.maximize_page_icon = assetsPath("maximize_page.png")

    # 定义软件当前版本
    self.APP_VERSION = '1.0.0'
    self.APP_TITLE = '小灰妙记'
    self.APP_ICON_PATH = assetsPath('favicon.png')
    self.APP_DATA_DIRNAME = 'GreatNoteData'

    self.IS_DEBUG = False        #生产环境，使用远程服务器

    self.PING_HOST = 'greatnote.cn'
    self.filter_id = "leftBar"
    self.button_frame_id = "frame_13"
    self.button_container_id = "leftbar_container"
    self.button_close_id = "btn_close"
    self.button_login_id = "btn_login_icon"
    self.button_name_id = "btn_login_text"

    # 默认主题
    self.default_theme = {
      "skin": {
        "current_skin_index": 0
      },
      "skinStyle": [
        {
          "id": "skin001",
          "name": "\u9ed8\u8ba4",
          "header_bg_color": "#6a5acd",
          "main_bg_color": "#f0f0f0",
          "app_bg_image": assetsPath("skin", "app_bg_image_1.png"),
        },
        {
          "id": "skin002",
          "name": "\u73ca\u745a\u7ea2",
          "header_bg_color": "#cd5a5a",
          "main_bg_color": "#fffbcb",
          "app_bg_image": assetsPath("skin", "app_bg_image_2.png"),
        },
        {
          "id": "skin003",
          "name": "\u70ab\u9177\u9ed1",
          "header_bg_color": "#000",
          "main_bg_color": "#e4d5ff",
          "app_bg_image": assetsPath("skin", "app_bg_image_3.png"),
        }
      ]
    }