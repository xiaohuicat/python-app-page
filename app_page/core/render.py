import xml.etree.ElementTree as ET
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QScrollArea, QLayout, QVBoxLayout, QComboBox)
from mako.template import Template
from ..utils import setWidgetStyle, unescape_xml, t2d, decode


# 组件类型别名映射
aliasWidgetMap = {
  # 基础组件
  'div': 'QWidget',
  'widget': 'QWidget',
  'label': 'QLabel',
  'button': 'QPushButton',
  'line-edit': 'QLineEdit',
  'text-edit': 'QPlainTextEdit',
  'selector': 'QComboBox',
  'checkbox': 'QCheckBox',
  'radio': 'QRadioButton',
  # 布局相关
  'grid': 'QGridLayout',
  'h-box': 'QHBoxLayout',
  'v-box': 'QVBoxLayout',
  'form': 'QFormLayout',
  'stacked': 'QStackedLayout',
  'graphics-anchor': 'QGraphicsAnchorLayout',
  'graphics-grid': 'QGraphicsGridLayout',
  'graphics-layout': 'QGraphicsLayout',
  'graphics-linear': 'QGraphicsLinearLayout',
}


# 渲染模板
def render(parent:QWidget|QLayout, template:str, params:dict={}) -> dict:
  """渲染模板

  参数:
      parent (object): 父布局或父组件
      template (str): 模板字符串

  返回:
      widgetIdMap(dict): 组件id与组件的映射关系
      vnode(dict): 虚拟节点
  """
  widgetIdMap:dict = {}
  xml_template:str = Template(template).render(**params)
  vnode:dict = template_to_vnode(xml_template)
  # 如果父组件是布局，并且需要滚动，则创建一个滚动布局
  if vnode.get('scroll', False):
    parent = create_scroll_layout(parent)
  return vnode_render(parent, vnode, widgetIdMap)


# 递归渲染组件
def vnode_render(parent:QWidget|QLayout, vnode:dict, widgetIdMap:dict) -> dict:
  vnodes = vnode.get('children', [])
  if len(vnodes) == 0:
    return
  for props in vnodes:
    if isinstance(props, dict) and 'type' in props:
      widget:QWidget|QLayout = create_widget(parent, props)
      set_attributes(widget, props, widgetIdMap)
  return widgetIdMap


# 创建组件
def create_widget(parent:QWidget|QLayout, props:dict) -> QWidget|QLayout:
  AutoWidget:QWidget|QLayout = getattr(QtWidgets, props['type']) if hasattr(QtWidgets, props['type']) else None
  # 如果上一个层级是布局，则直接添加组件，否则以上一个组件为父组件创建组件或布局
  if AutoWidget and isinstance(parent, QLayout):
    widget:QWidget = AutoWidget()
    if 'grid' in props:
      grid = props['grid']
      parent.addWidget(widget, *grid)
    else:
      parent.addWidget(widget)
  else:
    widget:QWidget|QLayout = AutoWidget(parent)
  return widget


# 设置组件属性
def set_attributes(widget:QWidget|QLayout, props:dict, widgetIdMap:dict):
  for key in props.keys():
    value = props[key]
    if key == 'id':
      widget.setObjectName(value)
      widgetIdMap[value] = widget
    elif key == 'text':
      if isinstance(widget, QtWidgets.QPlainTextEdit):
        widget.setPlainText(unescape_xml(value))
        return
      widget.setText(unescape_xml(value))
    elif key == 'title':
      if hasattr(widget, 'setToolTip'):
        widget.setToolTip(unescape_xml(value))
    elif key == 'style':
      if isinstance(value, str):
        widget.setStyleSheet(value)
      elif callable(value):
        value(widget)
      else:
        setWidgetStyle(widget, value, cover=True)
    elif key == 'margins':
      widget.setContentsMargins(*value)
    elif key == 'spacing':
      widget.setSpacing(value)
    elif key == 'width':
      widget.setFixedWidth(value)
    elif key == 'height':
      widget.setFixedHeight(value)
    elif key == 'disabled':
      if hasattr(widget, 'setReadOnly'):
        widget.setReadOnly(value)
    elif key == 'placeholder':
      if hasattr(widget, 'setPlaceholderText'):
        widget.setPlaceholderText(unescape_xml(value))
    elif key == 'password':
      if hasattr(widget, 'setEchoMode'):
        widget.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
    elif key == 'align':
      if hasattr(widget, 'setAlignment') and hasattr(Qt, value):
        widget.setAlignment(getattr(Qt, value))
    elif key == 'scroll':
      if isinstance(widget, QLayout) and value:
        widget.__scroll_layout = create_scroll_layout(widget)
    elif key == 'options':
      if isinstance(widget, QComboBox):
        widget.addItems(value)
    elif key == 'children':
      if hasattr(widget, '__scroll_layout'):
        parent = widget.__scroll_layout
        delattr(widget, '__scroll_layout')
      else:
        parent = widget
      vnode_render(parent, props, widgetIdMap)


# 预处理
def preprocess(item:dict, key:str, value:str):
  if key == 'margins' or key == 'grid':
    item[key] = list(map(int, value.strip("[]").split(',')))
  elif key == 'options':
    # 尝试解析json数组
    try:
      result = t2d(value)
    except:
      result = []
    item[key] = result
  elif key in ['spacing', 'width', 'height']:
    item[key] = int(value)
  elif key in ['scroll', 'disabled', 'scroll']:
    item[key] = value == 'True'
  else:
    item[key] = decode(value)


# 处理xml节点
def create_vnode(element) -> dict:
  # xml节点转换为组件字典
  vnode = {
    # 匹配组件别名
    'type': aliasWidgetMap[element.tag] if element.tag in aliasWidgetMap else element.tag,
  }

  # 预处理节点属性
  for key in element.attrib.keys():
    preprocess(vnode, key, element.attrib.get(key))
  
  # 判断是否有children
  if len(element) > 0:
    vnode['children'] = []

  # 递归处理子节点
  for child in element:
    child_component = create_vnode(child)
    vnode['children'].append(child_component)

  return vnode
  

# 将xml模板转换为虚拟节点
def template_to_vnode(template:str) -> dict:
  """将xml模板转换为组件列表。

  参数:
      template (str): xml模板

  返回:
      components(list): 组件列表
  """
  # 将xml字符串转换为字典
  return create_vnode(ET.fromstring(template))


# 创建可滚动布局
def create_scroll_layout(layout:QLayout, style:str="background-color: transparent;"):
  scroll_area = QScrollArea()
  scroll_area.setWidgetResizable(True)
  scroll_area.setStyleSheet(style)
  content_widget = QWidget()
  scroll_area.setWidget(content_widget)
  content_layout = QVBoxLayout(content_widget)
  content_layout.setContentsMargins(0, 0, 0, 0)
  layout.addWidget(scroll_area)
  return content_layout