from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QMenu
from PySide6.QtGui import QIcon
from .MoveEventMechine import MoveEventMechine


MENU_STYLE = """
QMenu {
  border: 1px solid #f0f0f0; /* 边框宽度为1px，颜色为#CCCCCC */
  border-radius: 10px; /* 边框圆角 */
  background-color: #FAFAFC; /* 背景颜色 */
  font-size: 14px;
  color: #666;
  padding: 10px 0px 10px 0px; /* 菜单项距菜单顶部边界和底部边界分别有5px */

}

QMenu::item { /* 菜单子控件item，为菜单项在default的状态 */
  border: 0px solid transparent;
  background-color: transparent;
  min-width: 100px;
  min-height: 30px;
  padding: 0px 10px;
}

QMenu::icon { padding: 0px 10px; }

QMenu::item:selected { /* 为菜单项在selected的状态 */
  background-color: #EDEDEF;
}

QMenu::item:disabled{ /* 为菜单项在disabled的状态 */
  color: #CCCCCC;
  background: none;
}

QMenu::separator { /* 菜单子控件separator，定义菜单项之间的分隔线 */
  height: 1px;
  background: #CCCCCC;
  margin-left: 2px; /* 距离菜单左边界2px */
  margin-right: 2px; /* 距离菜单右边界2px */
}

QMenu::right-arrow { /* 菜单子控件right-arrow，定义子菜单指示器 */
  width: 24px;
  height: 24px;
  image: url(:/Resource/right_arrow);
}

QMenu::left-arrow { /* 菜单子控件left-arrow，定义子菜单指示器 */
  width: 24px;
  height: 24px;
  image: url(:/Resource/left_arrow);
}

/*
QMenu::icon:checked {
  border: none;
  background-color: transparent;
  position: absolute;
  width: 24px;
  height: 24px;
}*/

QMenu::item::indicator { /* 菜单项子控件indicator，定义菜单项在选中状态下的指示器 */
  width: 24px;
  height: 24px;
}

QMenu::item::indicator:unchecked { /* 定义菜单项未选中的状态 */
  image: none;
}

QMenu::item::indicator:checked { /* 定义菜单项选中的状态 */
  image: url(:/Resource/checkebox);
}

QPushButton#PlayerButton { /* 自定义菜单项中的按钮 */
  border: none;
  background-color: transparent;
}

QPushButton#PlayerButton:hover {
  padding-top: 2px;
  padding-left: 2px;
}

QPushButton#PlayerButton:pressed {
  padding: 0px;
}

"""


class CallMenu:
  def __init__(self, target:QWidget, itemList:list, type:str='left'or'right'or'both') -> None:
    self.target = target if target else QWidget()
    self.itemList = itemList
    self.initMenu(type)
    self.initAnimation()
    if type != 'left':
      self.target.contextMenuEvent = self.contextMenuEvent
  
  def show(self, event):
    pos = event.globalPos()
    self.target._left_contextMenu.exec_(pos)

  def contextMenuEvent(self, event):
    pos = event.globalPos()
    self.target._right_contextMenu.exec_(pos)
  
  def initAnimation(self):
    pass

  def initMenu(self, type:str):
    menu = QMenu(self.target)
    if type == 'left':
      self.target._left_contextMenu = menu
    elif type == 'right':
      self.target._right_contextMenu = menu
    elif type == 'both':
      self.target._left_contextMenu = menu
      self.target._right_contextMenu = menu
    else:
      raise Exception("type error")

    for each in self.itemList:
      try:
        menu.addAction(QIcon(each["icon"]), each["name"], each["callback"])
      except Exception as e:
        print("initMenu error: ", e)
    self.itemList = []
    
    menu.setWindowFlag(Qt.NoDropShadowWindowHint)  # 去除阴影效果
    menu.setWindowFlag(Qt.FramelessWindowHint)  # 去除原来的边框
    menu.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景

    menu.setStyleSheet(MENU_STYLE)
    


class Click_Menu:
  def __init__(self, target:QWidget, itemList:list, type:str='left'or'right'or'both'):
    self.right_click = CallMenu(target, itemList, type)
    self.mechine = MoveEventMechine(target, self.right_click.show, type)
    target.mousePressEvent = self.mechine.start
    target.mouseMoveEvent = self.mechine.clear
    target.mouseReleaseEvent = self.mechine.stop
  
  def destroy(self):
    self.mechine.target.mousePressEvent = None
    self.mechine.target.mouseMoveEvent = None
    self.mechine.target.mouseReleaseEvent = None
    self.mechine.target = None
    self.mechine.callback = None
    self.mechine.isClick = None
    self.mechine = None
    self.right_click = None



class RightClick_Menu:
  def __init__(self, target:QWidget, itemList:list):
    self.right_click = CallMenu(target, itemList, type='right')

  def destroy(self):
    self.right_click = None



class Click_RightClick_Menu:
  def __init__(self, target:QWidget, itemList:list):
    self.right_click = CallMenu(target, itemList, type='both')
    self.mechine = MoveEventMechine(target, self.right_click.show, type="both")
    target.mousePressEvent = self.mechine.start
    target.mouseMoveEvent = self.mechine.clear
    target.mouseReleaseEvent = self.mechine.stop
  
  def destroy(self):
    self.mechine.target.mousePressEvent = None
    self.mechine.target.mouseMoveEvent = None
    self.mechine.target.mouseReleaseEvent = None
    self.mechine.target = None
    self.mechine.callback = None
    self.mechine.isClick = None
    self.mechine = None
    self.right_click = None