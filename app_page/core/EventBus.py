from PySide6.QtWidgets import QWidget

# 事件总线
class EventBus(object):
  def __init__(self, widgets:dict={}, hasSelf=False):
    self.widgets:dict = widgets
    self.hasSelf = hasSelf
    self._disconnectList = []

  def getWidget(self, id:str):
    return self.widgets.get(id, None)


  def register(self, id:str, signal:str, callback):
    widget:QWidget = self.getWidget(id)
    widget_dict = widget.__dict__
    signalInstance = widget_dict[signal]
    if hasattr(signalInstance, 'connect'):
      new_callback = (lambda *args: callback(self, *args)) if self.hasSelf else callback
      signalInstance.connect(new_callback)
    if hasattr(signalInstance, 'disconnect'):
      def disconnect():
        try:
          if widget:
            signalInstance.disconnect(new_callback)
        except:
          pass
      self._disconnectList.append(disconnect)


  def clear(self):
    #  清理组件映射表
    keys = list(self.widgets.keys())
    for key in keys:
      del self.widgets[key]
    
    self.widgets = {}
    #  清理所有注册的事件
    for disconnect in self._disconnectList:
      disconnect()
    self._disconnectList = []