from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent

class MoveEventMechine:
  def __init__(self, target, callback, type="both"):
    self.target = target
    self.callback = callback
    self.isClick = None
    self.type = type
  
  def start(self, event:QMouseEvent):
    self.isClick = True
  
  def clear(self, event:QMouseEvent):
    self.isClick = False
    QPushButton.mouseMoveEvent(self.target, event)
  
  def stop(self, event:QMouseEvent):
    if self.isClick:
      if self.type == "left" and event.button() == Qt.LeftButton:
        self.callback(event)
      elif self.type == "right" and event.button() == Qt.RightButton:
        self.callback(event)
      elif self.type == "both":
        self.callback(event)
      elif self.type != "left" and self.type != "right" and self.type != "both":
        raise Exception("button must be left or right or both")