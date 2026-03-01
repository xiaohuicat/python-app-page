import requests, re, json

MCP_DICT = {
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
        "description": "写入内容到本地文件，path是文件路径，content是要写入的字符串内容，一般写入成功即可结束任务。"
    }
}

TAIL_TEXT = '\r\n\r\n非常重要：工具调用必须按这个格式"[TOOL] <tool_name> <JSON_PARAMS> [TOOL END]"，其中<JSON_PARAMS>必须是合法JSON字符串，如"[TOOL] read_file {"path":"/Users/my_project/readme.md"} [TOOL END]"，不要解析，否则无法调用工具！！！'

def extract_tool_call(reply: str, mcp_dict):
    pattern = r'\[TOOL\]\s*(.+?)\s*\[TOOL END\]'
    match = re.search(pattern, reply.strip(), re.DOTALL | re.MULTILINE)
    
    if not match:
        return None, None

    tool_content = match.group(1).strip()
    if '{' not in tool_content:
        raise ValueError(f"工具调用格式错误，缺少参数部分: {tool_content}")
    
    tool_name_part, params_json_part = tool_content.split('{', 1)
    tool_name = tool_name_part.strip()
    params_json_str = '{' + params_json_part
    
    if '}' in params_json_str:
        params_json_str = params_json_str[:params_json_str.rindex('}') + 1]
    
    if tool_name not in mcp_dict:
        raise ValueError(f"工具调用错误: 未知工具 {tool_name}")
    
    try:
        params = json.loads(params_json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"工具 {tool_name} 的参数不是合法的JSON字符串: {e}")

    if not isinstance(params, dict):
        raise ValueError(f"工具 {tool_name} 的参数必须是一个JSON对象（键值对），当前解析结果: {params}")

    required_params = set(mcp_dict[tool_name]["param"])
    if not required_params.issubset(params.keys()):
        missing = required_params - params.keys()
        raise ValueError(f"工具 {tool_name} 缺少必要参数: {missing}")

    return tool_name, params

def create_tool_description(mcp_dict):
    tool_descriptions = []
    for tool_name, tool_info in mcp_dict.items():
        params = ",".join([f"\"{each}\":\"XXX\"" for each in tool_info["param"]])
        desc = tool_info["description"]
        example_call = f"[TOOL] {tool_name} {{{params}}} [TOOL END]"
        tool_descriptions.append(f"工具: {tool_name} 作用: {desc} 调用格式: {example_call}")

    return "\n\n".join(tool_descriptions)

def create_system_prompt(mcp_dict, has_tail=True):
    tail_text = '' if has_tail else TAIL_TEXT
    return f"""
你是一个专业的开发助理，你可以调用以下工具：

{create_tool_description(mcp_dict)}

调用规则：
1. 你需要根据用户输入判断是否调用工具，调用哪个工具；如果需要，必须严格按照上述“调用格式”输出，不要加任何多余文字
2. 工具调用必须以按照以下格式，"[TOOL] <tool_name> <JSON_PARAMS> [TOOL END]"，如"[TOOL] read_file {{"path":"/Users/my_project/readme.md"}} [TOOL END]"。
3. 如果不需要调用工具，请直接给出简洁、专业、像开发助理的回答。
4. 若工具调用错误后续不再继续调用，提醒用户失败原因。
5. 若工具调用成功继续完成后续任务，解决用户问题。
5. 参数为路径时必须是绝对路径。{tail_text}"""

class DevAgent:
    def __init__(self, call_api, mcp_dict=MCP_DICT, max_steps=5, log=print, history_mode=True, has_tail=True):
        self.log = log
        self.mcp_dict = mcp_dict
        self.call_api = call_api
        self.max_steps = max_steps
        self.history_mode = history_mode
        self.has_tail = has_tail
        self.tool_results = []
        self.messages = [{"role": "system", "content": create_system_prompt(self.mcp_dict, has_tail=self.has_tail)}]

    def call_mcp(self, name, payload) -> str:
        url = self.mcp_dict[name]["url"]
        try:
            resp = requests.post(url, json=payload, timeout=10)
            return resp.json()['data']
        except Exception as e:
            return f"{name}工具调用失败: {str(e)}"

    def call_ai(self, prompt:str = None) -> str:
        if self.history_mode:
            messages = []
            for msg in self.messages:
                if self.has_tail and isinstance(msg.get('content'), str) and TAIL_TEXT in msg['content']:
                    msg['content'] = msg['content'].replace(TAIL_TEXT, '')
                item = msg.copy()
                messages.append(item)
            
            if prompt is not None:
                msg = {"role": "user", "content": prompt + TAIL_TEXT if self.has_tail else prompt}
                self.messages.append(msg)
                messages.append(msg)
            
        else:
            messages = [
                {"role": "system", "content": create_system_prompt(self.mcp_dict)},
                {"role": "user", "content": prompt + TAIL_TEXT if self.has_tail else prompt},
            ]
        resp = self.call_api(messages)
        return resp.strip()

    def chat(self, user_input: str) -> str:
        current_query = user_input
        step = 0

        while step < self.max_steps:
            self.log(f"\r\n🧠 AI 思考中... (步骤 {step + 1})")
            ai_reply = self.call_ai(current_query)
            self.messages.append({"role": "assistant", "content": ai_reply})

            try:
                tool_name, payload = extract_tool_call(ai_reply, self.mcp_dict)
                # 如果没有工具调用，直接返回AI回答作为最终结果
                if tool_name is None:
                    self.log(f"\r\n✅ AI 最终回答：{ai_reply}")
                    return ai_reply
                # 如果有工具调用，执行工具并将结果反馈给AI继续下一轮对话
                self.log(f"\r\n🔍 解析工具调用：工具={tool_name} 参数={payload}")
                tool_result = self.call_mcp(tool_name, payload)
                self.tool_results.append((tool_name, payload, tool_result))
                self.messages.append({"role": "user", "content": f"调用工具 {tool_name} 的返回结果: {tool_result}"})
            except Exception as e:
                self.log(f"⚠️ 工具调用失败: {e}")
                self.messages.append({"role": "user", "content": f"工具调用失败: {e}"})

            if not self.history_mode:
                tool_results_str = "\r\n\r\n".join(
                    f"  - 你调用了工具: {entry[0]}, 返回结果: {entry[2]}"
                    for entry in self.tool_results
                )
                current_query = (
                    f"用户最初的问题：{user_input}\r\n\r\n"
                    f"工具调用历史：\n{tool_results_str}"
                )
            else:
                current_query = None
            
            step += 1
        
        return f"❌ 超过最大工具调用次数（{self.max_steps}次），已终止。可能陷入循环或任务过于复杂。"
    
    def reset(self):
        self.tool_results.clear()
        self.messages = [{"role": "system", "content": create_system_prompt(self.mcp_dict, has_tail=self.has_tail)}]