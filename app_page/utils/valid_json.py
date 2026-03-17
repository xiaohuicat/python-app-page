import re, json

def get_valid_json(json_str: str) -> dict:
    """
    验证并获取有效的JSON对象
    :param json_str: 待验证的JSON字符串
    :return: 解析后的Python字典
    :raises: ValueError 如果JSON格式无效
    """
    if not json_str:
        raise ValueError("JSON字符串不能为空")
    
    # 清理字符串中的特殊字符和空白符
    cleaned_str = json_str.strip()
    
    # 移除可能存在的注释（// 或 /* */ 格式）
    # 移除单行注释
    cleaned_str = re.sub(r'//.*?$', '', cleaned_str, flags=re.MULTILINE)
    # 移除以/*开头以*/结尾的多行注释
    cleaned_str = re.sub(r'/\*.*?\*/', '', cleaned_str, flags=re.DOTALL)
    
    try:
        # 解析JSON字符串
        json_obj = json.loads(cleaned_str)
        
        # 确保解析结果是字典类型
        if not isinstance(json_obj, dict):
            raise ValueError("JSON内容必须是一个对象（字典）")
        
        return json_obj
    
    except json.JSONDecodeError as e:
        # 更友好的错误提示
        error_msg = f"JSON解析错误: {str(e)}"
        # 尝试定位错误位置
        if hasattr(e, 'pos') and e.pos > 0:
            error_msg += f"，错误位置：第{e.pos}个字符"
        raise ValueError(error_msg)
    except Exception as e:
        raise ValueError(f"JSON验证失败: {str(e)}")

def format_json(json_obj, indent: int = 2, ensure_ascii: bool = False) -> str:
    """
    格式化JSON对象为易读的字符串
    :param json_obj: Python字典对象
    :param indent: 缩进空格数，默认2
    :param ensure_ascii: 是否确保ASCII编码，默认False（支持中文）
    :return: 格式化后的JSON字符串
    """
    if json_obj is None:
        return ""
    
    try:
        # 如果输入是字符串，先尝试解析
        if isinstance(json_obj, str):
            json_obj = get_valid_json(json_obj)
        
        # 格式化JSON字符串
        formatted_str = json.dumps(
            json_obj,
            indent=indent,
            ensure_ascii=ensure_ascii,
            sort_keys=False,  # 保持原有键的顺序
            separators=(',', ': ')
        )
        
        return formatted_str
    
    except Exception as e:
        # 如果格式化失败，返回原始内容并提示
        if isinstance(json_obj, str):
            return json_obj
        raise ValueError(f"JSON格式化失败: {str(e)}")