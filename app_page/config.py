import os
def assetsPath(*args):
    """获取资源路径
    Args:
        args (tuple): 目录，文件名

    Returns:
        path (str): 资源绝对路径
    """
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", *args)

tips_ui = assetsPath("tips.ui")
tipsBox_ui = assetsPath("tipsBox.ui")
MainWindow_ui = assetsPath("main.ui")
loading_icon = assetsPath("loading.gif")
small_page_icon = assetsPath("small_page.png")
maximize_page_icon = assetsPath("maximize_page.png")

# 定义软件当前版本
APP_VERSION = '1.0.0'
APP_TITLE = '小灰妙记'
APP_ICON_PATH = assetsPath('favicon.png')
APP_DATA_DIRNAME = 'GreatNoteData'

IS_DEBUG = False        #生产环境，使用远程服务器

PING_HOST = 'greatnote.cn'

filter_id = "leftBar"
button_frame_id = "frame_13"
button_container_id = "leftbar_container"
button_close_id = "btn_close"
button_login_id = "btn_login_icon"
button_name_id = "btn_login_text"

# 默认主题
default_theme = {
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