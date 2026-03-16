from PySide6.QtWidgets import QWidget


# 事件总线
class EventBus(object):
  def __init__(self, widget_id_map:dict={}, has_self=False):
    self.widget_id_map:dict = widget_id_map
    self.has_self = has_self
    self._disconnectList = []


  def setWidgets(self, widget_id_map:dict):
    self.widget_id_map = widget_id_map


  def getWidget(self, id:str):
    return self.widget_id_map.get(id, None)


  def register(self, id:str, signal:str, callback):
    widget:QWidget = self.getWidget(id)
    widget_dict = widget.__dict__
    signalInstance = widget_dict[signal]
    if hasattr(signalInstance, 'connect'):
      new_callback = (lambda *args: callback(self, *args)) if self.has_self else callback
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
    keys = list(self.widget_id_map.keys())
    for key in keys:
      del self.widget_id_map[key]
    
    self.widget_id_map = {}
    #  清理所有注册的事件
    for disconnect in self._disconnectList:
      disconnect()
    self._disconnectList = []