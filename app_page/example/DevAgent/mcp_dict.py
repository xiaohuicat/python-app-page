mcp_dict = {
  "store_text": {
    "url": "http://127.0.0.1:8080/store_text",
    "description": "存储文本内容，参数text是要存储的文本字符串，调用成功后会返回一个8位提取码，其它工具若支持可以直接输入提取码来获取文本内容。适用于需要存储较长文本内容的场景，避免直接在工具调用中传输过长文本导致解析困难。",
    "usage": "[TOOL STORE TEXT START]和[TOOL STORE TEXT END]标签包裹的文本就是要存储的内容",
  },
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
    "description": "写入内容到本地文件。file_path是文件路径；content是要写入的字符串内容，支持直接输入提取码"
  },
  "delete_file": {
    "url": "http://127.0.0.1:8080/delete_file",
    "param": ["file_path"],
    "description": "删除本地文件，file_path是文件路径"
  },
  "download_file": {
    "url": "http://127.0.0.1:8080/download_file",
    "param": ["url", "save_path"],
    "description": "下载文件到本地，url是文件链接，save_path是要保存的本地路径"
  },
  "search_files": {
    "url": "http://127.0.0.1:8080/search_files",
    "param": ["pattern", "path", "max_results"],
    "description": "按模式搜索文件，pattern是搜索模式，path是搜索路径（默认当前目录），max_results是最大返回结果数（默认100）"
  },
  "system_info": {
    "url": "http://127.0.0.1:8080/system_info",
    "param": [],
    "description": "获取系统信息，如CPU、内存、磁盘、处理器型号、内存大小、硬盘使用情况等"
  },
  "list_processes": {
    "url": "http://127.0.0.1:8080/list_processes",
    "param": [],
    "description": "列出所有运行中的进程信息"
  },
  "kill_process": {
    "url": "http://127.0.0.1:8080/kill_process",
    "param": ["pid", "force"],
    "description": "终止指定PID的进程，pid是进程ID，force是否强制杀死（默认false）"
  },
  "run_shell_command": {
    "url": "http://127.0.0.1:8080/run_shell_command",
    "param": ["command", "timeout", "cwd"],
    "description": "执行Shell命令，command是要执行的命令，timeout超时时间（默认30秒），cwd工作目录"
  },
  "network_info": {
    "url": "http://127.0.0.1:8080/network_info",
    "param": [],
    "description": "获取网络接口、路由、端口等网络信息"
  },
  "view_logs": {
    "url": "http://127.0.0.1:8080/view_logs",
    "param": ["log_path", "lines"],
    "description": "查看日志文件内容，log_path是日志文件路径，lines是读取行数（默认100）"
  },
  "get_weather": {
    "url": "http://127.0.0.1:8080/get_weather",
    "param": ["province_name", "city_name", "include_sections"],
    "description": "获取天气信息，province_name是省份名称，city_name是城市名称，include_sections为包含天气分段信息[\"实时天气\", \"未来7天预报\", \"空气质量\", \"温度趋势\", \"气候参考\"]，（若为空列表[]，则返回全部信息）"
  },
  "draw_image": {
    "url": "http://127.0.0.1:8080/draw_image",
    "param": ["prompt", "size"],
    "description": "根据提示词生成图像，prompt是提示词，size是图像大小（支持1328*1328）"
  },
}