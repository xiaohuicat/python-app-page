from ..core import Page
from PySide6.QtWidgets import QStackedWidget


class Stack(Page):
  def __init__(self, id:str='stackedWidget'):
    super().__init__()
    self.id = id

  def getStack(self) -> QStackedWidget:
    return self.mainWin.getWidget(self.id)

  def setCurrentPage(self, index):
    return self.getStack().setCurrentIndex(index)

  def count(self):
    return self.getStack().count()

  def getPageByIndex(self, index):
    return self.getStack().widget(index)

  def getIndexById(self, id):
    count = self.count()
    for i in range(count):
      if self.getPageByIndex(i).objectName() == id:
        return i
    return -1

  def getPageById(self, id):
    return self.getPageByIndex(self.getIndexById(id))

  def addWidget(self, widget):
    return self.getStack().addWidget(widget)

  def insertWidget(self, index, widget):
    return self.getStack().insertWidget(index, widget)
