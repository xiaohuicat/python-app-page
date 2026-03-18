from PySide6.QtWidgets import QWidget


class EventBus(object):
  """
  事件总线
  """
  def __init__(self, widget_id_map:dict={}):
    self.widget_id_map:dict = widget_id_map
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
      signalInstance.connect(callback)
    if hasattr(signalInstance, 'disconnect'):
      def disconnect():
        try:
          if widget:
            signalInstance.disconnect(callback)
        except:
          pass
      self._disconnectList.append(disconnect)


  def clear(self):
    keys = list(self.widget_id_map.keys())
    for key in keys:
      del self.widget_id_map[key]
    
    self.widget_id_map = {}
    for disconnect in self._disconnectList:
      disconnect()
    self._disconnectList = []