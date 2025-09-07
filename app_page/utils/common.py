import os, shutil, time
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
    # 确保目标目录的父目录存在
    os.makedirs(os.path.dirname(appPath), exist_ok=True)
    # 检查源路径是否存在
    if os.path.exists(packagePath):
      try:
        # 复制文件或目录
        if os.path.isfile(packagePath):
          shutil.copy(packagePath, appPath)
        else:
          shutil.copytree(packagePath, appPath, dirs_exist_ok=True)
      except Exception as e:
        raise SystemError("复制文件或目录时出错", e)
    else:
      print("源路径不存在:", packagePath)
  
  return appPath

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

