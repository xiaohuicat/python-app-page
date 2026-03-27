from PySide6.QtWidgets import QWidget, QLayout, QLineEdit, QPlainTextEdit
from PySide6.QtGui import QIcon
from app_page_core import Store
from .EventBus import EventBus
from .render.render_main import render
from ..utils import assetsPath
from .common import updateStyle


class WidgetManager:
  """
  组件控制类
    提供组件的注册、获取、设置样式、设置类名、设置父组件等操作
  """
  def __init__(self, parent:QWidget=None, template:str=None, params:dict=None) -> None:
    """
    初始化组件管理器
      :param parent: QWidget 父组件
      :param template: str 模板名称
      :param params: dict 参数
    """
    if parent:
      render_dict = render(parent, template, params)
      widget_list, widget_id_map = render_dict.get('widget_list', None), render_dict.get('widget_id_map', None)
    else:
      widget_list, widget_id_map = [], {}

    self.__widget_list = widget_list if widget_list else []
    self.__widget_id_map = widget_id_map if widget_id_map else {}
    self.__eventBus = EventBus(self.__widget_id_map)


  def getWidget(self, id:str) -> QWidget|QLayout:
    return self.__widget_id_map.get(id, None) if type(id) is str else self.__widget_id_map


  def getWidgets(self) -> dict:
    return self.__widget_id_map


  def setWidgets(self, widget_id_map:dict) -> None:
    self.__widget_id_map = widget_id_map
    self.__eventBus.setWidgets(widget_id_map)


  def setWidgetList(self, widget_list:list) -> None:
    self.__widget_list = widget_list


  def setIcon(self, id:str, *args) -> None:
    widget:QWidget = self.getWidget(id)
    if not widget:
      return
    if hasattr(widget, 'setIcon'):
      widget.setIcon(QIcon(assetsPath(*args)))


  def setClass(self, id:str, className:str, immediate:bool = True, updateWidget:QWidget|None = None) -> None:
    widget:QWidget = self.getWidget(id)
    if not widget:
      return
    widget.setProperty('class', className)
    if immediate:
      updateStyle(updateWidget if updateWidget else widget)


  def register(self, id:str, signal:str, callback) -> None:
    if not self.getWidget(id):
      return
    self.__eventBus.register(id, signal, callback)


  def getText(self, id:str) -> str:
    widget:QWidget = self.getWidget(id)
    if not widget:
      return ''
    if isinstance(widget, QLineEdit):
      return widget.text()
    if isinstance(widget, QPlainTextEdit):
      return widget.toPlainText()


  def setText(self, id:str, value:str) -> None:
    widget:QWidget = self.getWidget(id)
    if not widget:
      return
    if isinstance(widget, QLineEdit):
      widget.setText(value)
    elif isinstance(widget, QPlainTextEdit):
      widget.setPlainText(value)


  def destroy(self) -> None:
    event_filter = Store().get('APP_EVENT_FILTER', None)
    for each in self.__widget_list:
      try:
        if hasattr(each, 'has_event_filter') and each.has_event_filter and event_filter:
          each.removeEventFilter(event_filter)
          delattr(each, 'has_event_filter')
        if hasattr(each, 'deleteLater'):
          each.deleteLater()
      except Exception as e:
        print(f"Widget delete error: {e}")
    self.__eventBus.clear()
    self.__widget_id_map = {}