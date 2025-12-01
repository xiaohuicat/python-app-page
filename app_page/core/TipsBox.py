from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from app_page_core import Callback, Param, Store
from ..animation import FadeEffect, MoveWin, Shadow
from ..core.Setting import getSetting
from ..utils import loadUI

class TipsBox(QWidget):
  def __init__(self, topic:str="更新提醒", title:str="提示窗的标题", content:str="提示的内容"):
    super().__init__()
    self.callback = Callback()
    param:Param = Store().get("param")
    MoveWin(self, param, id="tips_box_position")
    
    ui = getSetting("tipsBox_ui")
    # 如果ui是字符串
    if isinstance(ui, str):
        self.ui = loadUI(ui)
        # 创建垂直布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
    else:
        self.ui = ui()
        self.ui.setupUi(self)

    self.fadeEffect = FadeEffect(self, 100, self.close)

    Shadow(self.ui.container)

    self.ui.cancle.clicked.connect(self.click("cancle"))
    self.ui.confirm.clicked.connect(self.click("confirm"))
    self.ui.btn_close.clicked.connect(self.fadeEffect.close)

    self.setTopic(topic)
    self.setTitle(title)
    self.setContent(content)

    # 设置弹出窗口的位置
    # self.setGeometry(pos[0], pos[1], 200, 100)
    self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)  # 设置窗口置顶

    self.setWindowFlag(Qt.FramelessWindowHint)  # 去除原来的边框
    self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景


  def click(self, name):
    def func():
      if name != "close":
        self.callback.run(name)
      self.fadeEffect.close()
    return func
  

  def show(self):
    self.fadeEffect.show()
    super().show()


  # 输入相对坐标
  def setPos(self,pos_main_win):
    pos=[pos_main_win[0]+580, pos_main_win[1]+70]
    self.setGeometry(pos[0], pos[1], 224, 324)


  # 设置用户名
  def setTopic(self, text):
    self.setWindowTitle(text)


  # 设置用户名
  def setTitle(self, text):
    self.ui.msg_title.setText(text)


  # 设置用户名
  def setContent(self, text):
    self.ui.msg_content.setText(text)


  def setStyle(self,url,color):
    if url and color:
      self.ui.setStyleSheet("""
        background-color: """+color+""";
        border-image: url('"""+url+"""');
        border-radius: 16px;
      """)
    elif url:
      self.ui.setStyleSheet("""
        border-image: url('"""+url+"""');
        border-radius: 16px;
      """)
    elif color:
      self.ui.setStyleSheet("""
        background-color: """+color+""";
        border-radius: 16px;
      """)
    else:
      self.ui.setStyleSheet("""
        background-color: #6a5acd;
        border-radius: 16px;
      """)


  def windowStateChanged(self, oldState, newState):
    super().windowStateChanged(oldState, newState)
    if newState:
      print("Window lost focus")  # 输出窗口失去焦点


  def closeEvent(self, event: QCloseEvent) -> None:
    self.callback.run("close")
    return super().closeEvent(event)
