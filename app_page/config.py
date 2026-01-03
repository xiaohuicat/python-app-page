from .utils import assetsPath
from .core import Page


class Config():
  def __init__(self):
    self.tipsBox_ui = assetsPath("UI", "tipsBox.ui")

    # 定义软件当前版本
    self.APP_VERSION = '1.0.0'
    self.APP_TITLE = '小灰妙记'
    self.APP_ICON_PATH = assetsPath('icon', 'favicon.png')
    self.APP_DATA_DIRNAME = 'GreatNoteData'

    self.IS_DEBUG = True        #生产环境，使用远程服务器
    self.SETUP_EASY = False

    self.PING_HOST = 'greatnote.cn'
    self.filter_id = "leftBar"
    self.button_container_id = "leftbar_container"

    # 默认主题
    self.default_theme = {
      "skinId": 'skin001',
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
    
    self.pages = {
      "chat": Page,
      "setting": Page,
      "message": Page,
    }
    
    self.pageOptionList = [
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
        "name": "信息",
        "id": "message",
        "filter": "right_top_bar",
        "icon": "assets/icon/right_top_bar/message.png",
        "stack_id": "app_page_message"
      }
    ]