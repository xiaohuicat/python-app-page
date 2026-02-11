import requests

DASHSCOPE_API_KEY = "sk-**************************"
QWEN_MODEL = "qwen-turbo"

def call_qwen(messages, api_key=DASHSCOPE_API_KEY, model=QWEN_MODEL, temperature=0.7):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "input": {
            "messages": messages
        },
        "parameters": {
            "temperature": temperature,
        }
    }

    try:
        resp = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            headers=headers,
            json=payload,
            timeout=30
        )
    except Exception as e:
        return f"网络请求异常：{str(e)}"

    result = resp.json()

    if resp.status_code != 200:
        error_msg = result.get("message", "未知错误")
        print("❌ API 错误详情：", result)
        return f"模型调用失败（HTTP {resp.status_code}）：{error_msg}"

    try:
        return result["output"]["text"]
    except KeyError:
        print("❌ 响应中缺少 'output.text'，完整响应：", result)
        return "模型返回格式异常，请检查 API Key 是否有效。"