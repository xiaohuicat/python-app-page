import requests, re, json

DASHSCOPE_API_KEY = "sk-**************************"
QWEN_MODEL = "qwen-turbo"


mcp_dict = {
    "read_project": {
        "url": "http://127.0.0.1:8080/list_dir",
        "param": ["path"],
        "description": "读取本地项目目录的markdown结构树",
    },
    "read_file": {
        "url": "http://127.0.0.1:8080/read_file",
        "param": ["file_path"],
        "description": "读取本地文件内容，返回文件内容字符串"
    },
    "write_file": {
        "url": "http://127.0.0.1:8080/write_file",
        "param": ["file_path", "content"],
        "description": "写入内容到本地文件，path是文件路径，content是要写入的字符串内容"
    }
}


class DevAgent:
    def __init__(self, mcp_dict, call_api):
        self.mcp_dict = mcp_dict
        self.call_api = call_api
        self.tool_history = []
  
    def call_mcp(self, name, payload):
        """调用 MCP 工具"""
        try:
            url = self.mcp_dict[name]["url"]
            resp = requests.post(url, json=payload, timeout=10)
            return resp.json()['data']
        except Exception as e:
            return f"{name}工具调用失败: {str(e)}"

    def call_ai(self, prompt=None):
        system_prompt = f"""
你是一个专业的开发助理，你可以调用以下工具：

{create_tool_description(self.mcp_dict)}

规则：
1. 根据需要判断是否调用工具。如果需要，必须严格按照上述“调用格式”输出，不要加任何多余文字、解释或 Markdown。
2. 工具调用必须以 "[TOOL] " 开头，"[TOOL] <tool_name> <JSON_PARAMS>"，如"[TOOL] read_file {{"path"="/Users/my_project/readme.md"}}"。
3. 如果不需要调用工具，请直接给出简洁、专业、像开发助理的回答。
4. 若工具调用错误后续不再继续调用，提醒用户失败原因。
5. 参数为路径时必须是绝对路径。
"""     
        print("\r\n----->prompt：", prompt)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        resp = self.call_api(messages)
        print("\r\n----->🧠 AI 回复：", resp)
        return resp.strip()  # 防止多余空格干扰解析

    def chat(self, user_input):
        """主聊天入口：支持多轮工具调用，直到 AI 给出最终回答"""
        current_query = user_input
        max_steps = 5  # 防止无限循环
        step = 0

        while step < max_steps:
            print(f"\r\n🧠 AI 思考中... (步骤 {step + 1})")
            ai_reply = self.call_ai(current_query)

            # 尝试解析是否为工具调用
            try:
                tool_name, payload = extract_tool_call(ai_reply, self.mcp_dict)
            except Exception as e:
                print(f"⚠️ 工具调用格式错误: {e}")
                return ai_reply  # 直接返回原始回复

            # 如果没有工具调用，说明是最终回答
            if tool_name is None:
                print(f"\r\n✅ AI 最终回答：{ai_reply}")
                return ai_reply

            # 否则执行工具调用
            print(f"\r\n🔍 解析工具调用：工具={tool_name} 参数={payload}")
            tool_result = self.call_mcp(tool_name, payload)
            self.tool_history.append((tool_name, payload, tool_result))
            # 构造工具调用历史的可读字符串（从上到下逐条列出）
            tool_history_str = "\r\n".join(
                f"  - 你调用了工具: {entry[0]}, 返回结果: {entry[2]}"
                for entry in self.tool_history
            )
            # 构造下一轮输入
            current_query = (
                f"用户最初的问题：{user_input}\r\n"
                f"工具调用历史：\n{tool_history_str}"
            )
            step += 1
        
        return "❌ 超过最大工具调用次数（5次），已终止。可能陷入循环或任务过于复杂。"


def extract_tool_call(reply: str, mcp_dict):
    """
    从 AI 回复中提取工具调用信息。
    新格式: [TOOL] tool_name {"param1": "value1", "param2": "value with spaces"}
    返回: (tool_name, params_dict) 或 (None, None)
    """
    # 匹配 [TOOL] 后跟工具名和一个 JSON 字符串（允许前后有空格）
    pattern = r'^\[TOOL\]\s+(\w+)\s+(.+)$'
    match = re.match(pattern, reply.strip())
    if not match:
        return None, None

    tool_name = match.group(1)
    if tool_name not in mcp_dict:
        return None, None  # 未知工具

    json_str = match.group(2).strip()
    try:
        params = json.loads(json_str)
    except json.JSONDecodeError:
        return None, None  # JSON 格式非法

    if not isinstance(params, dict):
        return None, None  # 参数必须是对象（字典）

    # 检查是否包含所有必需参数
    required_params = set(mcp_dict[tool_name]["param"])
    if not required_params.issubset(params.keys()):
        missing = required_params - params.keys()
        raise ValueError(f"工具 {tool_name} 缺少必要参数: {missing}")

    return tool_name, params


def create_tool_description(mcp_dict):
    # 动态生成工具描述
    tool_descriptions = []
    for tool_name, tool_info in mcp_dict.items():
        params = ",".join([f"\"{each}\":\"XXX\"" for each in tool_info["param"]])
        desc = tool_info["description"]
        example_call = f"[TOOL] {tool_name} {{{params}}}"
        tool_descriptions.append(f"工具: {tool_name} 作用: {desc} 调用格式: {example_call}")

    return "\n\n".join(tool_descriptions)


def call_qwen(messages):
    """调用千问大模型（DashScope 新版 API）"""
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": QWEN_MODEL,
        "input": {
            "messages": messages
        },
        "parameters": {
            "temperature": 0.1
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

    # 处理非 200 响应
    if resp.status_code != 200:
        error_msg = result.get("message", "未知错误")
        print("❌ API 错误详情：", result)
        return f"模型调用失败（HTTP {resp.status_code}）：{error_msg}"

    # 安全提取 output.text
    try:
        return result["output"]["text"]
    except KeyError:
        print("❌ 响应中缺少 'output.text'，完整响应：", result)
        return "模型返回格式异常，请检查 API Key 是否有效。"


if __name__ == "__main__":
    # 帮我检查***目录结构，如果有todo.txt文件则读取完成里面的任务
    agent = DevAgent(mcp_dict, call_qwen)
    print("🚀 千问开发助理已启动（输入 exit 退出）")
    while True:
        try:
            user = input("\n你：").strip()
            if user.lower() in ["exit", "quit"]:
                print("👋 再见！")
                break
            if not user:
                continue
            agent.chat(user)
        except KeyboardInterrupt:
            print("\n👋 中断退出。")
            break