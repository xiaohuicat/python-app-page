from typing import Union, Dict, Any
from PySide6.QtCore import Qt
from ...utils import unescape_xml
from ..common import setShadowEffect
from .common import getWidget
from app_page_core import Store
from PySide6 import QtWidgets
from PySide6.QtWidgets import (QWidget, QScrollArea, QLayout, QVBoxLayout, QGridLayout,
                                QComboBox, QPlainTextEdit, QLineEdit)


def render_widget(parent:QWidget|QLayout, vnode:dict):
    widgetList = []
    widgetIdMap = {}
    # 如果父组件是布局，并且需要滚动，则创建一个滚动布局
    if 'scroll' in vnode:
        option = vnode.get('scroll', {})
        parent = create_scroll_layout(parent, option, widgetList, widgetIdMap)
    # 递归渲染组件，并返回组件id映射表
    return vnode_render(parent, vnode, widgetList, widgetIdMap)


# 创建可滚动布局
def create_scroll_layout(layout:QLayout, option:dict, widgetList:list, widgetIdMap:dict):
    scroll_area = QScrollArea()
    id = option.get('id', None)
    if id:
        scroll_area.setObjectName(id)
        scroll_area.setProperty('id', id)
        widgetIdMap[id] = scroll_area
    scroll_area.setWidgetResizable(True)
    style = option.get('style', None)
    if style:
        scroll_area.setStyleSheet(style)
    widgetList.append(scroll_area)
    content_widget = QWidget()
    widgetList.append(content_widget)
    scroll_area.setWidget(content_widget)
    layout_type = getWidget(option.get('layout', 'v-box'))
    if layout_type and hasattr(QtWidgets, layout_type):
        Layout = getattr(QtWidgets, layout_type)
        content_layout = Layout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)
        return content_layout
    else:
        raise ValueError('不存在的布局')


# 递归渲染组件
def vnode_render(parent:QWidget|QLayout, vnode:dict, widgetList:list, widgetIdMap:dict) -> tuple:
    vnodes = vnode.get('children', [])
    if len(vnodes) == 0:
        return
    for props in vnodes:
        if isinstance(props, dict) and 'type' in props:
            widget:QWidget|QLayout = create_widget(parent, props)
            widgetList.append(widget)
            set_attributes(widget, props, widgetList, widgetIdMap)
    return widgetList, widgetIdMap


# 创建组件
def create_widget(parent:QWidget|QLayout, props:dict) -> QWidget|QLayout:
    type_name = props.get('type')
    if not type_name:
        raise ValueError("Props must contain a 'type' key.")
    AutoClass:QWidget|QLayout = getattr(QtWidgets, type_name, None)
    if AutoClass is None:
        raise TypeError(f"Unknown Qt type: {type_name}")
    
    if AutoClass and isinstance(parent, QLayout):
        # 如果上一个层级是布局，则直接添加组件
        widget:QWidget = AutoClass()
        if 'grid' in props and isinstance(parent, QGridLayout):
            grid = props['grid']
            parent.addWidget(widget, *grid)
        else:
            parent.addWidget(widget)
    else:
        # 否则以上一个组件为父组件创建组件或布局
        widget:QWidget|QLayout = AutoClass(parent)
    return widget


def set_attributes(
    widget: Union[QWidget, QLayout],
    props: Dict[str, Any],
    widget_list: list,
    widget_id_map: Dict[str, Union[QWidget, QLayout]]
) -> None:
    """设置组件属性
    
    Args:
        widget: 要设置属性的组件或布局
        props: 属性字典
        widget_id_map: 组件ID映射表
    """
    # 处理特殊属性的映射表：属性名 -> 处理函数
    prop_handlers = {
        'id': lambda v: _set_id(widget, v, widget_id_map),
        'text': lambda v: _set_text(widget, v),
        'title': lambda v: _set_title(widget, v),
        'style': lambda v: _set_style(widget, v),
        'margins': lambda v: _set_margins(widget, v),
        'spacing': lambda v: _set_spacing(widget, v),
        'width': lambda v: _set_fixed_width(widget, v),
        'height': lambda v: _set_fixed_height(widget, v),
        'disabled': lambda v: _set_disabled(widget, v),
        'visible': lambda v: _set_visible(widget, v),
        'placeholder': lambda v: _set_placeholder(widget, v),
        'password': lambda v: _set_password(widget),
        'align': lambda v: _set_alignment(widget, v),
        'scroll': lambda v: _set_scroll(widget, v, widget_list, widget_id_map),
        'options': lambda v: _set_options(widget, v),
        'shadow': lambda v: _set_shadow(widget, v),
        'children': lambda v: _set_children(widget, props, widget_list, widget_id_map),
        'event-filter': lambda v: _set_event_filter(widget, v),
    }

    for key, value in props.items():
        # 优先使用专用处理器
        if key in prop_handlers:
            prop_handlers[key](value)
        # 处理通用属性
        else:
            widget.setProperty(key, value)


# 以下为属性处理的辅助函数
def _set_id(widget: Union[QWidget, QLayout], value: str, widget_id_map: dict) -> None:
    """处理ID属性"""
    widget.setObjectName(value)
    widget.setProperty('id', value)
    widget_id_map[value] = widget


def _set_text(widget: Union[QWidget, QLayout], value: str) -> None:
    """处理文本属性"""
    unescaped_value = unescape_xml(value)
    if isinstance(widget, QPlainTextEdit):
        widget.setPlainText(unescaped_value)
    elif hasattr(widget, 'setText'):
        widget.setText(unescaped_value)


def _set_title(widget: Union[QWidget, QLayout], value: str) -> None:
    """处理标题/提示属性"""
    if hasattr(widget, 'setToolTip'):
        widget.setToolTip(unescape_xml(value))


def _set_style(widget: Union[QWidget, QLayout], value: str) -> None:
    """处理样式属性"""
    if hasattr(widget, 'setStyleSheet'):
        widget.setStyleSheet(value)


def _set_margins(widget: Union[QWidget, QLayout], value: list) -> None:
    """处理边距属性"""
    if hasattr(widget, 'setContentsMargins'):
        widget.setContentsMargins(*value)


def _set_spacing(widget: Union[QWidget, QLayout], value: int) -> None:
    """处理间距属性"""
    if hasattr(widget, 'setSpacing'):
        widget.setSpacing(value)


def _set_fixed_width(widget: Union[QWidget, QLayout], value: int) -> None:
    """处理宽度属性"""
    if hasattr(widget, 'setFixedWidth'):
        widget.setFixedWidth(value)


def _set_fixed_height(widget: Union[QWidget, QLayout], value: int) -> None:
    """处理高度属性"""
    if hasattr(widget, 'setFixedHeight'):
        widget.setFixedHeight(value)


def _set_disabled(widget: Union[QWidget, QLayout], value: bool) -> None:
    """处理禁用属性"""
    if hasattr(widget, 'setReadOnly'):
        widget.setReadOnly(value)
    # 补充：通常禁用组件使用setEnabled
    if hasattr(widget, 'setEnabled'):
        widget.setEnabled(not value)


def _set_visible(widget: Union[QWidget, QLayout], value: bool) -> None:
    """处理可见性属性"""
    if hasattr(widget, 'setVisible'):
        widget.setVisible(value)


def _set_placeholder(widget: Union[QWidget, QLayout], value: str) -> None:
    """处理占位符属性"""
    if hasattr(widget, 'setPlaceholderText'):
        widget.setPlaceholderText(unescape_xml(value))


def _set_password(widget: Union[QWidget, QLayout]) -> None:
    """处理密码框属性"""
    if hasattr(widget, 'setEchoMode'):
        widget.setEchoMode(QLineEdit.Password)


def _set_alignment(widget: Union[QWidget, QLayout], value: str) -> None:
    """处理对齐属性"""
    if hasattr(widget, 'setAlignment') and hasattr(Qt, value):
        widget.setAlignment(getattr(Qt, value))


def _set_scroll(widget: Union[QWidget, QLayout], value: dict, widget_list: list,
    widget_id_map: dict) -> None:
    """处理滚动属性"""
    if isinstance(widget, QLayout):
        widget.__scroll_layout = create_scroll_layout(widget, value, widget_list, widget_id_map)


def _set_options(widget: Union[QWidget, QLayout], value: list) -> None:
    """处理选项属性（下拉框）"""
    if isinstance(widget, QComboBox):
        widget.addItems(value)


def _set_shadow(widget: Union[QWidget, QLayout], value: Any) -> None:
    """处理阴影效果属性"""
    setShadowEffect(widget, value)


def _set_children(
    widget: Union[QWidget, QLayout],
    props: dict,
    widget_list: list,
    widget_id_map: dict
) -> None:
    """处理子组件属性"""
    if hasattr(widget, '__scroll_layout'):
        parent = widget.__scroll_layout
        delattr(widget, '__scroll_layout')
    else:
        parent = widget
    vnode_render(parent, props, widget_list, widget_id_map)
    
def _set_event_filter(widget: Union[QWidget, QLayout], value: Any) -> None:
    widget.setProperty('event-filter', value)
    event_filter = Store().get('APP_EVENT_FILTER', None)
    if not event_filter:
        print('无法监听event-filter', value)
        return
    widget.installEventFilter(event_filter)
    widget.has_event_filter = True