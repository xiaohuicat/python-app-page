from PySide6.QtWidgets import QWidget, QLayout
from .render_vnode import render_vnode
from .render_widget import render_widget


# 渲染模板
def render(parent:QWidget|QLayout, template:str, params:dict={}) -> dict:
    """渲染模板

    参数:
        parent (QWidget|QLayout): 父布局或父组件
        template (str): 模板字符串
        params (dict): 模板参数字典

    返回:
        dict: 包含以下字段的字典
            - vnode (dict): 虚拟节点
            - widget_id_map (dict): 组件id与组件的映射关系
            - widget_list (list): 所有生成的组件列表
    """
    vnode:dict = render_vnode(template, params)
    widget_list, widget_id_map = render_widget(parent, vnode)
    return {'vnode': vnode, 'widget_id_map': widget_id_map, 'widget_list': widget_list}