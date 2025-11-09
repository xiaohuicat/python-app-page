import os
from typing import Dict, List, Union, Any, Optional
from PySide6.QtWidgets import QWidget
from app_page_core import Store, Param
from .common import assetsPath


create_default_theme = lambda: {
    "skinId": 'skin001',
    "skinStyle": [
        {
            "id": "skin001",
            "name": "\u9ed8\u8ba4",
            "header_bg_color": "#6a5acd",
            "main_bg_color": "#f0f0f0",
            "app_bg_image": assetsPath("skin", "app_bg_image_1.png"),
        },
        {
            "id": "skin002",
            "name": "\u73ca\u745a\u7ea2",
            "header_bg_color": "#cd5a5a",
            "main_bg_color": "#fffbcb",
            "app_bg_image": assetsPath("skin", "app_bg_image_2.png"),
        },
        {
            "id": "skin003",
            "name": "\u70ab\u9177\u9ed1",
            "header_bg_color": "#000",
            "main_bg_color": "#e4d5ff",
            "app_bg_image": assetsPath("skin", "app_bg_image_3.png"),
        }
    ]
}

def setAppStyle(target: Any) -> None:
    """
    根据参数设置应用程序的整体样式
    
    Args:
        target: 目标对象，包含param属性
        default_theme: 默认主题配置
    """
    default_theme = create_default_theme()
    setting = Param(target.param.pathJoin("userPath", "setting.json"), default_theme)
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
    setWidgetStyleById(widget_id='app_header', style={"background-color": style['header_bg_color']}, cover=True)
    setWidgetStyleById(widget_id='app_main', style={
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
    mainWin = store.get('mainWin')
    if not mainWin:
        raise Exception("mainWin object not found in store")
    
    widget = mainWin.getWidget(widget_id)
    if not widget:
        raise Exception(f"widget_id = [{widget_id}] not found in mainWin")
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
