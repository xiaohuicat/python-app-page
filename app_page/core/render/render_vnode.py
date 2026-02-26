import json
from typing import Any, Dict, List, Union, Optional
import xml.etree.ElementTree as ET
from mako.template import Template
from ...utils import t2d, decode
from .common import getWidget


def render_vnode(template, params:dict={}):
    xml_template:str = Template(template).render(**params)
    xml_tree:dict = ET.fromstring(xml_template)
    vnode:dict = create_vnode(xml_tree)
    return vnode


# 处理xml节点
def create_vnode(element) -> dict:
    # xml节点转换为组件字典
    vnode = {'type': getWidget(element.tag)}

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


# 预处理
def preprocess(item: Dict[str, Any], key: str, value: str) -> None:
    """
    优化后的预处理函数：将字符串值按key类型转换为对应的数据结构
    
    Args:
        item: 要更新的字典
        key: 要处理的键名
        value: 要处理的字符串值
    """
    # 空值快速处理
    if not value or value.strip() in ("", "null", "None"):
        item[key] = None
        return

    # 定义类型处理映射：键分组 -> 处理逻辑
    type_handlers = {
        # 处理需要转换为四元素列表的键（数字字符串自动扩展为四元素）
        "four_element_list": {
            "keys": ["margins", "grid"],
            "handler": lambda v: _parse_four_element_list(v)
        },
        # 处理JSON数组类型的键
        "json_array": {
            "keys": ["options", "size-policy"],
            "handler": lambda v: _safe_parse_json(v, default=lambda *args:[])
        },
        # 处理JSON字典类型的键
        "json_dict": {
            "keys": ["shadow", "scroll"],
            "handler": lambda v: _safe_parse_json(v, default=lambda *args:{})
        },
        # 处理整数类型的键
        "integer": {
            "keys": ["spacing", "width", "height"],
            "handler": lambda v: _safe_parse_int(v)
        },
        # 处理布尔类型的键（修复原函数重复的scroll键）
        "boolean": {
            "keys": ["disabled", "visible"],
            "handler": lambda v: _safe_parse_bool(v)
        }
    }

    # 匹配对应的处理逻辑并执行
    for handler_info in type_handlers.values():
        if key in handler_info["keys"]:
            item[key] = handler_info["handler"](value)
            return

    # 默认处理：解码字符串
    item[key] = decode(value.strip())


def _safe_parse_int(value: str) -> Optional[int]:
    """安全解析整数，失败返回None"""
    try:
        return int(value.strip())
    except (ValueError, TypeError):
        return None


def _safe_parse_bool(value: str) -> bool:
    """安全解析布尔值，支持大小写不敏感的True/False字符串"""
    normalized_val = value.strip().lower()
    return normalized_val == "true"


def _safe_parse_json(value: str, default:callable) -> Any:
    """安全解析JSON字符串，失败返回默认值"""
    try:
        ret = t2d(value)
        if isinstance(ret, str):
            return default()
        return ret
    except (json.JSONDecodeError, TypeError):
        return default()


def _parse_four_element_list(value: str) -> List[int]:
    """
    解析四元素列表：
    - 输入为数字字符串（如"10"）→ 扩展为 [10, 10, 10, 10]
    - 输入为逗号分隔的字符串（如"10,20,30,40"）→ 转换为对应列表
    - 解析失败返回空列表
    """
    try:
        # 去除首尾空格和可能的[]括号
        cleaned_val = value.strip().strip("[]")
        # 分割为元素列表
        elements = [elem.strip() for elem in cleaned_val.split(",") if elem.strip()]
        
        # 转换为整数
        int_elements = list(map(int, elements))
        
        # 如果只有一个元素，扩展为四个相同值
        if len(int_elements) == 1:
            return int_elements * 4
        # 如果是四个元素，直接返回
        elif len(int_elements) == 4:
            return int_elements
        # 其他长度返回空列表（非法输入）
        else:
            return []
    except (ValueError, TypeError):
        return []