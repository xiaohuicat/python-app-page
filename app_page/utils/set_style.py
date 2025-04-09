import os
from typing import Dict, List, Union, Any, Optional
from PySide6.QtWidgets import QWidget
from app_page_core import Store
from .common import assetsPath


def setAppStyle(target: Any, default_theme: Dict[str, Any]) -> None:
    """
    根据参数设置应用程序的整体样式
    
    Args:
        target: 目标对象，包含param属性
        default_theme: 默认主题配置
    """
    setting = target.param.child(target.param.pathJoin("userPath", "setting.json"), default_theme)
    skin_id = setting.get("skinId", default_theme["skinId"])
    
    # 获取当前皮肤样式
    skin_styles = setting.get("skinStyle", default_theme['skinStyle'])
    style = next((s for s in skin_styles if s['id'] == skin_id), None)
    if not style:
        raise ValueError(f"Skin style with id '{skin_id}' not found")
    
    # 处理背景图片路径
    image_path = style['app_bg_image'].replace('\\', '/') if isinstance(style['app_bg_image'], str) else ''
    if not os.path.exists(image_path):
        image_path = assetsPath('skin', 'app_bg_image_1.png').replace('\\', '/')
    
    # 设置头部和主体样式
    setWidgetStyleById(widget_id='frame_header', style={"background-color": style['header_bg_color']}, cover=True)
    setWidgetStyleById(widget_id='frame_main', style={
        "background-color": style['main_bg_color'],
        "border-image": f"url('{image_path}') stretch",
    }, cover=True)


def setWidgetStyleById(widget_id: str, style: Dict[str, str], cover: bool = False) -> None:
    """
    通过ID设置控件的样式
    
    Args:
        widget_id: 控件的ID
        style: 样式字典
        cover: 是否覆盖现有样式
    
    Raises:
        Exception: 当UI对象未找到时
    """
    store = Store()
    ui = store.get('ui')
    if not ui:
        raise Exception("UI object not found in store")
    
    widget = ui[widget_id]
    _apply_style_to_widget(widget, style, widget_id, cover)


def setWidgetStyle(widget: QWidget, style: Union[Dict[str, str], List[Dict[str, str]]], 
                    widget_id: Optional[str] = None, cover: bool = False) -> None:
    """
    设置控件的样式
    
    Args:
        widget: 要设置样式的控件
        style: 样式字典或样式字典列表
        widget_id: 控件的ID（可选）
        cover: 是否覆盖现有样式
    """
    if isinstance(style, list):
        style = mergeStyles(*style)
    
    _apply_style_to_widget(widget, style, widget_id, cover)


def _apply_style_to_widget(widget: QWidget, style: Dict[str, str], 
                          widget_id: Optional[str] = None, cover: bool = False) -> None:
    """
    内部函数：将样式应用到控件
    
    Args:
        widget: 要设置样式的控件
        style: 样式字典
        widget_id: 控件的ID（可选）
        cover: 是否覆盖现有样式
    """
    style_sheet_list = []
    
    try:
        if not cover:
            current_style = widget.styleSheet()
            if current_style:
                style_sheet_list = current_style.split('\n')
    except Exception as e:
        print(f"Warning: Failed to get current style sheet: {e}")
    
    # 构建样式字符串
    if widget_id:
        style_str = f'#{widget_id}{{{";".join([f"{key}:{style[key]}" for key in style])}}}'
    else:
        style_str = ";".join([f"{key}:{style[key]}" for key in style])
    
    style_sheet_list.append(style_str)
    widget.setStyleSheet('\n'.join(style_sheet_list))


def mergeStyles(*style_dicts: Dict[str, str]) -> Dict[str, str]:
    """
    合并多个样式字典，后面的样式会覆盖前面的同名属性
    
    Args:
        *style_dicts: 要合并的样式字典列表
    
    Returns:
        合并后的样式字典
    """
    result = {}
    for style_dict in style_dicts:
        if isinstance(style_dict, dict):
            result.update(style_dict)
    return result


def s2t(*style_dicts: Dict[str, str]) -> str:
    """
    将样式字典转换为CSS样式字符串
    
    Args:
        *style_dicts: 要转换的样式字典列表
    
    Returns:
        CSS样式字符串
    """
    style = mergeStyles(*style_dicts)
    return ";".join([f"{key}:{style[key]}" for key in style])
