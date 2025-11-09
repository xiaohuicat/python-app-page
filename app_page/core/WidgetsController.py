from PySide6.QtWidgets import (QWidget, QLayout)
from PySide6.QtGui import QIcon
from ..core.EventBus import EventBus
from ..utils import assetsPath
from .common import updateStyle


class WidgetsController:
  def __init__(self, widgetIdMap:dict|None=None) -> None:
    self.__widgetIdMap = widgetIdMap if widgetIdMap else {}
    self.__eventBus = EventBus(self.__widgetIdMap)


  def getWidget(self, id:str) -> QWidget|QLayout:
    return self.__widgetIdMap.get(id, None) if type(id) is str else self.__widgetIdMap


  def getWidgets(self) -> dict:
    return self.__widgetIdMap


  def setWidgets(self, widgetIdMap:dict) -> None:
    self.__widgetIdMap = widgetIdMap
    self.__eventBus.setWidgets(widgetIdMap)


  def setIcon(self, id:str, *args) -> None:
    widget:QWidget = self.getWidget(id)
    if not widget:
      return
    if hasattr(widget, 'setIcon'):
      widget.setIcon(QIcon(assetsPath(*args)))


  def setClass(self, id:str, className:str) -> None:
    widget:QWidget = self.getWidget(id)
    if not widget:
      return
    widget.setProperty('class', className)
    updateStyle(widget)


  def register(self, id:str, signal:str, callback) -> None:
    if not self.getWidget(id):
      return
    self.__eventBus.register(id, signal, callback)


  def destroy(self) -> None:
    # 移除组件映射
    for key in self.__widgetIdMap.keys():
      try:
        widget:QWidget = self.__widgetIdMap[key]
        widget.deleteLater()
      except Exception as e:
        print(f"Widget delete error: {e}")
    self.__eventBus.clear()
    self.__widgetIdMap = {}