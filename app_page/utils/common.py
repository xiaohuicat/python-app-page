import os, shutil, time, json
from ..core import Setting


def assetsPath(*args):
  """获取资源路径
  Args:
      args (tuple): 目录，文件名

  Returns:
      path (str): 资源绝对路径
  """
  is_debug = Setting.getSetting("IS_DEBUG", False)
  packagePath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", *args)
  appPath = os.path.join(os.getcwd(), "assets", *args)
  if is_debug:
    print('appPath:', appPath)
    os.makedirs(os.path.dirname(appPath), exist_ok=True)
    # 源路径存在且目标路径不存在时才复制
    if os.path.exists(packagePath) and not os.path.exists(appPath):
      try:
        if os.path.isfile(packagePath):
          shutil.copy(packagePath, appPath)
        else:
          # 兼容Python 3.8以下版本（可添加版本判断）
          shutil.copytree(packagePath, appPath, dirs_exist_ok=True)
      except Exception as e:
        raise SystemError(f"复制资源失败（源：{packagePath}，目标：{appPath}）：{e}") from e
  
  return appPath


def assetsUrl(*args):
  """获取资源URL路径
  Args:
      args (tuple): 目录，文件名

  Returns:
      path (str): 资源绝对路径
  """
  return assetsPath(*args).replace("\\", "/")


def layout_clear(layout):
  """删除布局对象内所有子对象
  Args:
      layout (object): 布局对象
  """
  while layout.count():
    item = layout.takeAt(0)
    if item.widget():
      item.widget().deleteLater()
    elif item.layout():
      layout_clear(item.layout())


def timestamp():
  """毫秒级时间戳"""
  return int(time.time() * 1000)


def escape_xml(text):
  """转义XML字符"""
  return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;").replace('"', "&quot;")


def unescape_xml(text):
  """反转义XML字符"""
  return text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&apos;", "'").replace("&quot;", '"')


def d2t(data):
  """格式化JSON数据为字符串并转换为base64编码"""
  try:
    return json.dumps(data).encode('utf-8').hex()
  except Exception as e:
    return data


def t2d(text):
  """将base64编码的字符串转换为JSON数据"""
  try:
    return json.loads(bytes.fromhex(text).decode('utf-8'))
  except Exception as e:
    return text


def encode(text):
  """字符串编码为base64"""
  try:
    return '[#encode]:' + text.encode('utf-8').hex()
  except Exception as e:
    return text
  

def decode(text):
  """将base64字符串解码"""
  try:
    if text.startswith('[#encode]:'):
      return bytes.fromhex(text.replace('[#encode]:', '')).decode('utf-8')
    return text
  except Exception as e:
    return text 