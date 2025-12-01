import numpy as np
from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6 import QtCore
from PySide6 import QtGui
from app_page import Param
from ..core.EventHook import EventHook


class MoveWin(QMainWindow):
  def __init__(self, target:QMainWindow | QWidget, param:Param | None, id:str | None):
    super().__init__(target)
    target.mousePressEvent = self.mousePressEvent
    target.mouseMoveEvent = self.mouseMoveEvent
    target.mouseReleaseEvent = self.mouseReleaseEvent
    self.target = target
    self.target.center = self.center

    self.id = id
    self.m_flag = False
    self.param = param
    self.mouseMoveEventHook = EventHook(10)

    if self.param:
      self.window_position = param.get(id, None)
      if self.window_position and len(self.window_position) == 4:
          print('根据已有参数设置窗口位置', self.window_position)
          try:
            self.target.setGeometry(*self.window_position)
          except Exception as e:
            print("设置窗口位置失败！！！ e=",e)
      else:
          print('自动设置窗口位置')
          self.target.setFixedWidth(1080)
          self.target.setFixedHeight(753)
          self.center()
          rect = self.target.geometry()
          self.window_position = [rect.left(),rect.top(),rect.width(),rect.height()]
          self.target.setGeometry(*self.window_position)


  # 将窗口移动屏幕中央
  def center(self):
      qr = self.target.frameGeometry()
      cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
      qr.moveCenter(cp)
      self.target.move(qr.topLeft())


  def mousePressEvent(self, event):
    if event.button() == QtCore.Qt.LeftButton:
      self.m_flag = True
      self.m_Position = event.globalPos() - self.target.pos()  # 获取鼠标相对窗口的位置
      event.accept()
      self.target.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))  # 更改鼠标图标


  def mouseMoveEvent(self, mouse_event):
    if QtCore.Qt.LeftButton and self.m_flag:
      self.target.move(mouse_event.globalPos() - self.m_Position)   # 更改窗口位置
      self.mouseMoveEventHook.run(mouse_event.globalPos() - self.m_Position)
      mouse_event.accept()


  def mouseReleaseEvent(self, mouse_event):
    self.m_flag = False
    self.target.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
    self.setPosition()


  # 保存位置参数
  def setPosition(self, add=0):
      if not self.param:
        return
      rect = self.target.geometry()
      new_window_position = [rect.left(),rect.top(),rect.width() + add,rect.height() + add]
      self.window_position = new_window_position
      self.param.set(key=self.id, value=self.window_position)
