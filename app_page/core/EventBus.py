# 事件总线
class EventBus(object):
  def __init__(self, elements:dict={}, isSendSelf=True):
    self.elements:dict = elements
    self.isSendSelf = isSendSelf

  def getElement(self, id:str):
    return self.elements.get(id, None)

  def getConnect(self, id:str, event:str):
    item = self.getElement(id)
    if item:
      connectMap = {
        'clicked': hasattr(item, 'clicked') and hasattr(item.clicked, 'connect') and item.clicked.connect,
        'doubleClicked': hasattr(item, 'doubleClicked') and hasattr(item.doubleClicked, 'connect') and item.doubleClicked.connect,
        'pressed': hasattr(item, 'pressed') and hasattr(item.pressed, 'connect') and item.pressed.connect,
        'released': hasattr(item, 'released') and hasattr(item.released, 'connect') and item.released.connect,
        'hovered': hasattr(item, 'hovered') and hasattr(item.hovered, 'connect') and item.hovered.connect,
        'textChanged': hasattr(item, 'textChanged') and hasattr(item.textChanged, 'connect') and item.textChanged.connect,
        'valueChanged': hasattr(item, 'valueChanged') and hasattr(item.valueChanged, 'connect') and item.valueChanged.connect,
        'currentIndexChanged': hasattr(item, 'currentIndexChanged') and hasattr(item.currentIndexChanged, 'connect') and item.currentIndexChanged.connect,
      }
      return connectMap.get(event, None)

  def register(self, id:str, event:str, callback):
    connect = self.getConnect(id, event)
    if connect:
      if self.isSendSelf:
        connect(lambda *args: callback(self, *args))
      else:
        connect(lambda *args: callback(*args))

  def clear(self):
    keys = list(self.elements.keys())
    for key in keys:
      del self.elements[key]
    
    self.elements = {}