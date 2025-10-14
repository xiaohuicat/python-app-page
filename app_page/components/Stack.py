from ..core import Page


class Stack(Page):
  def __init__(self, id:str='stackedWidget'):
    super().__init__()
    self.id = id

  def setCurrentPage(self, index):
    return self.ui[self.id].setCurrentIndex(index)

  def count(self):
    return self.ui[self.id].count()

  def getPageByIndex(self, index):
    return self.ui[self.id].widget(index)

  def getIndexById(self, id):
    count = self.count()
    for i in range(count):
      if self.getPageByIndex(i).objectName() == id:
        return i
    return -1

  def getPageById(self, id):
    return self.getPageByIndex(self.getIndexById(id))

  def addWidget(self, widget):
    return self.ui[self.id].addWidget(widget)

  def insertWidget(self, index, widget):
    return self.ui[self.id].insertWidget(index, widget)
