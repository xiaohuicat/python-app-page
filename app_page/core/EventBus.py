# 事件总线
class EventBus(object):
  def __init__(self, widgets:dict={}, isSendSelf=True):
    self.widgets:dict = widgets
    self.isSendSelf = isSendSelf

  def getWidget(self, id:str):
    return self.widgets.get(id, None)

  def register(self, id:str, signal:str, callback):
    widget = self.getWidget(id)
    # 将对象的__dict__属性储存为一个字典
    widget_dict = widget.__dict__
    connect = widget_dict[signal].connect
    if self.isSendSelf:
      connect(lambda *args: callback(self, *args))
    else:
      connect(callback)

  def clear(self):
    keys = list(self.widgets.keys())
    for key in keys:
      del self.widgets[key]
    
    self.widgets = {}