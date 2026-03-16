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

SYSTEM_PROMPT = '''
调用规则：
1. 你需要根据用户输入判断是否调用工具，调用哪个工具；如果需要，必须严格按照上述“调用格式”输出，不要加任何多余文字
2. 工具调用除store_text外，必须以按照以下格式，"[TOOL] <tool_name> <JSON_PARAMS> [TOOL END]"，如"[TOOL] read_file {{"path":"/Users/my_project/readme.md"}} [TOOL END]"。
3. 工具调用store_text，必须以"[TOOL STORE TEXT START]"和"[TOOL STORE TEXT END]"标签包裹要存储的文本内容，如"[TOOL STORE TEXT START]这是要存储的文本内容[TOOL STORE TEXT END]"。
4. 调用工具的参数为路径时必须是绝对路径。
5. 如果不需要调用工具，请直接给出简洁、专业、像开发助理的回答。
6. 若工具调用错误后续不再继续调用，提醒用户失败原因。
7. 若工具调用成功认真判断后续操作，避免反复调用工具。
8. 调用工具返回的结果用户能看见你无需复述，只需要给出你觉得必要的回答。
'''
TAIL_TEXT = '\r\n\r\n非常重要：工具调用除store_text外，必须按这个格式"[TOOL] <tool_name> <JSON_PARAMS> [TOOL END]"，' \
'其中<JSON_PARAMS>必须是合法JSON字符串，如"[TOOL] read_file {"path":"/Users/my_project/readme.md"} [TOOL END]"，' \
'不要解析，否则无法调用工具！！！'

def extract_tool_call(reply: str, mcp_dict):
    """优化后的工具调用解析方法，更健壮的字符串处理"""
    # 使用更精确的正则表达式，匹配完整的工具调用格式
    pattern = r'\[TOOL\]\s*(\w+)\s*(\{.*?\})\s*\[TOOL END\]'
    match = re.search(pattern, reply.strip(), re.DOTALL)
    
    if not match:
        return None, None

    tool_name = match.group(1).strip()
    params_json_str = match.group(2).strip()
    
    if tool_name not in mcp_dict:
        raise ValueError(f"工具调用错误: 未知工具 {tool_name}")
    
    try:
        params = json.loads(params_json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"工具 {tool_name} 的参数不是合法的JSON字符串: {e}，参数内容={params_json_str}")

    if not isinstance(params, dict):
        raise ValueError(f"工具 {tool_name} 的参数必须是一个JSON对象（键值对），当前解析结果: {params}")

    return tool_name, params

def extract_store_text(text):
    """
    提取文本中被[TOOL STORE TEXT START]和[TOOL STORE TEXT END]标签包裹的内容
    保证提取的是最大范围的内容
    
    Args:
        text (str): 输入的文本内容
        
    Returns:
        str: 提取到的内容，如果标签不存在则返回空字符串
    """
    start_tag = "[TOOL STORE TEXT START]"
    end_tag = "[TOOL STORE TEXT END]"
    
    # 找到开始标签的位置
    start_index = text.find(start_tag)
    
    # 找到结束标签的位置
    end_index = text.rfind(end_tag)
    
    # 检查标签是否存在且顺序正确
    if start_index == -1 or end_index == -1 or start_index >= end_index:
        return ""
    
    # 提取两个标签之间的内容（不包含标签本身）
    content = text[start_index + len(start_tag):end_index].strip()
    
    return content

def create_tool_description(mcp_dict):
    tool_descriptions = []
    for tool_name, tool_info in mcp_dict.items():
        params = ",".join([f"\"{each}\":\"XXX\"" for each in tool_info["param"]]) if 'param' in tool_info else None
        desc = tool_info["description"] if 'description' in tool_info else None
        usage = f"[TOOL] {tool_name} {{{params}}} [TOOL END]" if 'usage' not in tool_info else tool_info['usage']
        tool_descriptions.append(f"工具: {tool_name} 作用: {desc} 调用格式: {usage}")

    return "\n\n".join(tool_descriptions)

def create_system_prompt(mcp_dict, system_prompt, has_tail=True):
    tail_text = '' if has_tail else TAIL_TEXT
    return f"""
你是一个专业和强大的开发助理，用户提问如果能通过工具解决，那么你就使用工具，减少继续提问用户，显得你专业和强大。你可以调用以下工具：

{create_tool_description(mcp_dict)}

{system_prompt}
{tail_text}"""

class DevAgent:
    def __init__(self, call_api, mcp_dict=MCP_DICT, max_steps=5, log=print, 
                 history_mode=True, has_tail=True, system_prompt=SYSTEM_PROMPT):
        self.log = log
        self.mcp_dict = mcp_dict
        self.call_api = call_api
        self.max_steps = max_steps
        self.history_mode = history_mode
        self.has_tail = has_tail
        self.tool_results = []
        self.messages = [
            {
                "role": "system", 
                "content": create_system_prompt(self.mcp_dict, system_prompt=system_prompt, has_tail=self.has_tail),
            }
        ]

    def call_mcp(self, name, payload) -> str:
        """优化后的工具调用方法，精细化异常处理"""
        if name not in self.mcp_dict:
            return f"{name}工具调用失败: 工具不存在"
        
        tool_info = self.mcp_dict[name]
        url = tool_info.get("url")
        if not url:
            return f"{name}工具调用失败: 未配置URL"
        
        timeout = tool_info.get("timeout", 10)
        
        # 参数校验
        required_params = tool_info.get("param", [])
        missing_params = [p for p in required_params if p not in payload]
        if missing_params:
            return f"{name}工具调用失败: 缺少必填参数 {missing_params}"
        
        try:
            resp = requests.post(url, json=payload, timeout=timeout)
            resp.raise_for_status()
            resp_dict = resp.json()
            return  resp_dict['result'] if 'result' in resp_dict else resp_dict
        except requests.exceptions.Timeout:
            return f"{name}工具调用失败: 请求超时（{timeout}秒）"
        except requests.exceptions.ConnectionError:
            return f"{name}工具调用失败: 连接拒绝，请检查服务是否启动"
        except requests.exceptions.HTTPError as e:
            return f"{name}工具调用失败: HTTP错误 {e.response.status_code} - {e.response.text}"
        except json.JSONDecodeError:
            return f"{name}工具调用失败: 接口返回非JSON格式，内容={resp.text}"
        except Exception as e:
            return f"{name}工具调用失败: 未知错误 {str(e)}"

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
                extract_text = extract_store_text(ai_reply)
                if extract_text != '':
                    tool_name = 'store_text'
                    payload = {'text': extract_text}
                else:
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