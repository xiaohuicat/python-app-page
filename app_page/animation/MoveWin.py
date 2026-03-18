from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6 import QtCore
from PySide6 import QtGui
from app_page_core import Store, Param
from ..core.EventHook import EventHook


class MoveWin(QMainWindow):
  """
  窗口/控件拖动功能增强类
    为指定的QMainWindow或QWidget添加鼠标拖动移动的功能，支持固定宽高限制
  """
  def __init__(self, target:QMainWindow | QWidget, move_id:str | None = None, fixed_w_h:tuple | None = None):
    """
    初始化拖动功能类
    
    Args:
        target (QMainWindow | QWidget): 要添加拖动功能的目标窗口或控件
        move_id (Optional[str]): 目标控件的标识（填了窗口可以独立移动）
        fixed_w_h (Optional[Tuple[int, int]]): 目标控件的固定宽高，格式为(宽度, 高度)
                                                None表示不限制控件宽高
    """
    super().__init__(target)
    target.mousePressEvent = self.mousePressEvent
    target.mouseMoveEvent = self.mouseMoveEvent
    target.mouseReleaseEvent = self.mouseReleaseEvent
    self.fixed_w_h = fixed_w_h
    self.target = target
    self.target.center = self.center

    self.m_flag = False
    self.move_id = move_id
    self.param:Param = Store().get('param', None)
    self.mouseMoveEventHook = EventHook(10)

    if self.move_id:
      self.window_position = self.param.get(move_id, None)
      if self.window_position and len(self.window_position) == 4:
        print('根据已有参数设置窗口位置', self.window_position)
        try:
          if self.fixed_w_h and len(self.fixed_w_h) == 2:
            self.target.setGeometry(*self.window_position[:2], *self.fixed_w_h)
          else:
            self.target.setGeometry(*self.window_position)
        except Exception as e:
          print("设置窗口位置失败！！！ e=",e)
      else:
        print('自动设置窗口位置')
        self.target.setFixedWidth(1080)
        self.target.setFixedHeight(753)
        self.center()
        rect = self.target.geometry()
        if self.fixed_w_h and len(self.fixed_w_h) == 2:
          self.window_position = [rect.left(),rect.top(),*self.fixed_w_h]
        else:
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
  def setPosition(self):
    if not self.move_id:
      return
    rect = self.target.geometry()
    new_window_position = [rect.left(),rect.top(),rect.width(),rect.height()]
    self.window_position = new_window_position
    if self.fixed_w_h and len(self.fixed_w_h) == 2:
      self.param.set(key=self.move_id, value=[*self.window_position[:2], *self.fixed_w_h])
    else:
      self.param.set(key=self.move_id, value=self.window_position)
