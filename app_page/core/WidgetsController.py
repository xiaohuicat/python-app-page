from PySide6.QtWidgets import (QWidget, QLayout)
from PySide6.QtGui import QIcon
from app_page_core import Store
from ..core.EventBus import EventBus
from ..utils import assetsPath
from .common import updateStyle


class WidgetsController:
  def __init__(self, widgetIdMap:dict|None=None) -> None:
    self.__widgetList = []
    self.__widgetIdMap = widgetIdMap if widgetIdMap else {}
    self.__eventBus = EventBus(self.__widgetIdMap)


  def getWidget(self, id:str) -> QWidget|QLayout:
    return self.__widgetIdMap.get(id, None) if type(id) is str else self.__widgetIdMap


  def getWidgets(self) -> dict:
    return self.__widgetIdMap


  def setWidgets(self, widgetIdMap:dict) -> None:
    self.__widgetIdMap = widgetIdMap
    self.__eventBus.setWidgets(widgetIdMap)


  def setWidgetList(self, widgetList:list) -> None:
    self.__widgetList = widgetList


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
    event_filter = Store().get('APP_EVENT_FILTER', None)
    # 移除组件映射
    for each in self.__widgetList:
      try:
        if hasattr(each, 'has_event_filter') and each.has_event_filter and event_filter:
          each.removeEventFilter(event_filter)
          delattr(each, 'has_event_filter')
        if hasattr(each, 'deleteLater'):
          each.deleteLater()
      except Exception as e:
        print(f"Widget delete error: {e}")
    self.__eventBus.clear()
    self.__widgetIdMap = {}