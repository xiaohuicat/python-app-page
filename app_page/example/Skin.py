from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton
from ..core import Page
from ..animation import RightClick_Menu
from ..config import Config
from ..utils import loadUI, setAppStyle, select_image, assetsPath


class SkinCard(Page):
  def __init__(self, option) -> None:
    super().__init__()
    self.option = option
    self.skin = loadUI(assetsPath('UI', 'skin_card.ui'))
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignTop)
    self.pick = QPushButton("", self.skin)
    self.pick.setFixedSize(260, 120)
    RightClick_Menu(self.pick, [
      {"name": "分享", "callback": self.shareSkin, "icon": assetsPath('menu', 'share.png')},
      {"name": "收藏", "callback": self.loveSkin, "icon": assetsPath('menu', 'love.png')},
      {"name": "更换壁纸", "callback": self.changeImage, "icon": assetsPath('menu', 'pictures.png')},
    ])
    layout.addWidget(self.pick)
    self.setStyle()

  def setup(self):
    super().setup()

    def callback():
      self.callback.run("pick", self.option)
    self.skin.status.clicked.connect(callback)
    self.pick.clicked.connect(callback)

  def setStyle(self):
    option = self.option
    self.pick.setStyleSheet("background-color: transparent;")
    self.skin.setStyleSheet("""#container {
      border-radius: 12px;
      border-image: url('"""+option['app_bg_image']+"""') stretch;
    }""")
    color = "red" if option["id"] == option["current"] else "transparent"
    self.skin.status.setStyleSheet("""
      background-color: """+color+""";
      border:1px solid #c0c0c0;
    """)
    self.skin.name.setText(option["name"])

  def changeStyle(self):
    pass

  def changeImage(self):
    output, _ = select_image(self.skin, assetsPath('skin'))
    
    # 保存背景图片路径
    setting = self.param.child(self.param.pathJoin("userPath","setting.json"), Config().default_theme)
    skinStyle = setting.get("skinStyle")
    skinStyle[self.option["index"]]["app_bg_image"] = output
    setting.save()
    setAppStyle(self)
    self.callback.run("update")

  def loveSkin(self):
    self.tips("已收藏", "success")

  def shareSkin(self):
    self.tips("正在开发")


class Skin(Page):
  def __init__(self):
    super().__init__()


  def setup(self):
    super().setup()
    color = ["rgb(255,58,58)", "rgba(255, 0, 0, 0.08)", "rgba(255, 0, 0, 0.05)"]
    self.ui.btn_skin_base.setStyleSheet(f"color: {color[0]}; border: 1px solid {color[1]}; background-color: {color[2]};")
  

  def reset(self):
    # 卡片layout是否被创建，若创建返回里面的卡片数量
    try:
      item_list = list(range(self.skin_layout.count()))
      self.children.remove()
    except:
      item_list = False

    # 若果卡片被创建
    if not item_list == False:
      item_list.reverse()# 倒序删除，避免影响布局顺序
      for i in item_list:
        item = self.skin_layout.itemAt(i)
        if item.widget():
          item.widget().deleteLater()
    else:
      self.skin_layout = QHBoxLayout(self.ui.skin_container)
      self.skin_layout.setAlignment(Qt.AlignTop)


  def show(self, *args):
    self.update()

  def hide(self, *args):
    self.children.remove()


  def update(self):
    self.reset()
    setting = self.param.child(self.param.pathJoin("userPath","setting.json"), Config().default_theme)
    self.current_skin_id = setting.get("skinId", Config().default_theme['skinId'])

    def pick(option):
      print('>>>pick:', option)
      if self.current_skin_id == option["id"]:
        return
      self.current_skin_id = option["id"]
      setting.set("skinId", option["id"])
      setting.save()
      setAppStyle(self, Config().default_theme)
      self.reset()
      render()
    
    def render():
      i = 0
      skinList = setting.get("skinStyle", [])
      for each in skinList:
        each['current'] = self.current_skin_id
        skincard = SkinCard(each)
        skincard.setup()
        skincard.callback.add("pick", pick)
        skincard.callback.add("update", self.update)
        self.children.add(f"skincard_{i}", skincard)
        self.skin_layout.addWidget(skincard.skin)
        i+=1

    render()