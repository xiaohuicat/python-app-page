import os
import dashscope

# 在终端执行: export DASHSCOPE_API_KEY="sk-..."
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
QWEN_MODEL = "qwen3.5-flash"

def call_qwen(messages, api_key=DASHSCOPE_API_KEY, model=QWEN_MODEL, temperature=0.7, **kwargs):
    try:
        # 调用多模态接口（兼容纯文本）
        response = dashscope.MultiModalConversation.call(
            api_key=api_key,
            model=model,
            messages=messages,
            temperature=temperature,
            **kwargs
        )
        
        # 检查请求是否成功
        if response.status_code != 200:
            return f"请求失败：状态码 {response.status_code}, 信息：{response.message}"

        # 【核心修复】安全地解析返回内容
        choices = response.output.get("choices", [])
        if not choices:
            return "请求成功但未返回任何内容 (choices为空)"
            
        message = choices[0].get("message", {})
        content = message.get("content")
        
        if content is None:
            return "返回内容为空"
        
        # 处理 content 可能是 字符串 或 列表 的情况
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # 遍历列表寻找 text 字段
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    return item["text"]
            # 如果没有找到 text 字段，返回整个列表的字符串表示或提示
            return f"未找到文本内容，返回结构: {content}"
        else:
            return f"未知的内容格式: {type(content)}"

    except Exception as e:
        # 捕获网络异常、SDK 内部错误等
        return f"请求发生异常：{str(e)}"