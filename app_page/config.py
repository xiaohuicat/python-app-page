import os

def createPath(name):
  return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", name)

tips_ui = createPath("tips.ui")
tipsBox_ui = createPath("tipsBox.ui")
MainWindow_ui = createPath("main.ui")
loading_icon = createPath("loading.gif")
small_page_icon = createPath("small_page.png")
maximize_page_icon = createPath("maximize_page.png")

# 定义软件当前版本
APP_VERSION = '1.0.0'
APP_TITLE = '小灰妙记'
APP_ICON_PATH = createPath('favicon.png')

IS_DEBUG = False        #生产环境，使用远程服务器

PING_HOST = 'greatnote.cn'

# 默认主题
default_theme = {
  "skin": {
    "current_skin_id": "skin001"
  },
  "skinStyle": [
    {
      "id": "skin001",
      "name": "\u9ed8\u8ba4",
      "header_bg_color": "#6a5acd",
      "main_bg_color": "#f0f0f0",
      "app_bg_image": "./assets/image/skin/1703964016891.png",
      "current": "skin001"
    },
    {
      "id": "skin002",
      "name": "\u73ca\u745a\u7ea2",
      "header_bg_color": "#cd5a5a",
      "main_bg_color": "#fffbcb",
      "app_bg_image": "./assets/image/skin/1703951087872.jpg",
      "current": "skin001"
    },
    {
      "id": "skin003",
      "name": "\u70ab\u9177\u9ed1",
      "header_bg_color": "#000",
      "main_bg_color": "#e4d5ff",
      "app_bg_image": "./assets/image/skin/1703951426046.jpg",
      "current": "skin001"
    }
  ]
}