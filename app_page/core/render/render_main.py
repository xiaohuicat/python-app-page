from PySide6.QtWidgets import (QWidget, QLayout)
from .render_vnode import render_vnode
from .render_widget import render_widget


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
  vnode:dict = render_vnode(template, params)
  widgets:dict = render_widget(parent, vnode)
  return {'vnode': vnode, 'widgets': widgets}