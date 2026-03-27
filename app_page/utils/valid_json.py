import json

def get_valid_json(text):
    """解析 JSON 字符串，确保结果为对象或数组。"""
    if not text:
        raise ValueError("输入字符串不能为空")
        
    try:
        data = json.loads(text)
        if not isinstance(data, (dict, list)):
            raise ValueError("JSON必须是对象或数组格式")
        return data
    except json.JSONDecodeError as e:
        start = max(0, e.pos - 15)
        end = min(len(e.doc), e.pos + 15)
        
        snippet = e.doc[start:end].replace('\n', ' ')
        pointer = " " * (e.pos - start) + "^"
        
        error_detail = (
            f"JSON语法错误: {e.msg}\n"
            f"位置: 第 {e.pos} 个字符\n"
            f"错误片段: {snippet}\n"
            f"          {pointer}"
        )
        raise ValueError(error_detail)

def compress_json(data):
    """将 JSON 对象压缩为紧凑格式字符串。"""
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)

def format_json(data):
    """将 JSON 对象格式化为易读字符串。"""
    return json.dumps(data, indent=4, ensure_ascii=False)