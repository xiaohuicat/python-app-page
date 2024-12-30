from PySide6 import QtCore
from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect

class Shadow:
  def __init__(self, target:QWidget):
    self.effect_shadow = QGraphicsDropShadowEffect(target)
    self.effect_shadow.setOffset(0,0) # 偏移
    self.effect_shadow.setBlurRadius(20) # 阴影半径
    self.effect_shadow.setColor(QtCore.Qt.gray) # 阴影颜色
    target.setGraphicsEffect(self.effect_shadow) # 将设置套用到widget窗口中