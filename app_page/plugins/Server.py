import json
from flask import Flask, request, Response
from app_page.plugins import FileTools  # 确保这个模块路径正确

app = Flask(__name__)

# 获取当前目录结构
@app.route('/list_dir', methods=['POST'])
def list_directory():
    # 获取 POST 请求的 JSON 数据
    data = request.get_json()
    if not data or 'path' not in data:
        return Response(
            json.dumps({"code": 1, "msg": "缺少 path 参数", "data": None}),
            mimetype='application/json'
        )

    target_path = data['path']
    print(f"正在加载目录: {target_path}")

    # 初始化 FileTools 实例
    file_tool = FileTools(target_path)

    # 加载目录，跳过指定文件夹
    file_tool.load({
        'skip_folders': [
            '__pycache__',
            '.DS_Store',
            'node_modules',
            'dist',
            'build',
            '.vscode',
            '.git',
        ]
    })

    print("目录加载完成，正在生成 Markdown 目录树...")
    # 获取 Markdown 格式的目录树（不显示大小和 MD5）
    md_tree = file_tool.print(show_size=False, show_md5=False)

    # 返回 JSON 响应
    response_data = {"code": 0, "msg": "成功", "data": md_tree}
    return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json')

# 读取文件/read_file
@app.route('/read_file', methods=['POST'])
def read_file():
    data = request.get_json()
    if not data or 'file_path' not in data:
        return Response(
            json.dumps({"code": 1, "msg": "缺少 file_path 参数", "data": None}),
            mimetype='application/json'
        )

    file_path = data['file_path']
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = f'读取{file_path}成功，文件内容如下：\n\n{content}'
        response_data = {"code": 0, "msg": "成功", "data": content}
    except Exception as e:
        response_data = {"code": 1, "msg": f"读取文件失败: {str(e)}", "data": None}

    return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json')

# 写入文件/write_file
@app.route('/write_file', methods=['POST'])
def write_file():
    data = request.get_json()
    if not data or 'file_path' not in data or 'content' not in data:
        return Response(
            json.dumps({"code": 1, "msg": "缺少 file_path 或 content 参数", "data": None}),
            mimetype='application/json'
        )

    file_path = data['file_path']
    content = data['content']
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        response_data = {"code": 0, "msg": "成功", "data": None}
    except Exception as e:
        response_data = {"code": 1, "msg": f"写入文件失败: {str(e)}", "data": None}

    return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)