import os, sys, hashlib, platform
from PySide6.QtGui import QGuiApplication
from win32com.shell import shell

# 获取屏幕信息
def getScreenInfo():
  result = []
  screens = QGuiApplication.screens()
  for each in screens:
    rect = each.geometry()
    result.append({
      'name': each.name(),
      'width': int(rect.width()*1.25),
      'height': int(rect.height()*1.25)
    })
  return result

# 检查网络连接
def internetConnection():
    import subprocess
    # host = 'baidu.com'
    host = 'greatnote.cn'
    # Determine the ping command based on the OS
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    
    # Build the command
    command = ['ping', param, '1', host]
    ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("ret code:", ret.returncode)
    return True if ret.returncode == 0 else False

# 检查权限
def check_permissions(file_path):
  try:
    # 检查文件是否存在
    if not os.path.exists(file_path):
      print(f"文件 '{file_path}' 不存在")
      return

    # 检查读取权限
    if os.access(file_path, os.R_OK):
      print(f"有读取权限: {file_path}")
    else:
      print(f"没有读取权限: {file_path}")

    # 检查写入权限
    if os.access(file_path, os.W_OK):
      print(f"有写入权限: {file_path}")
    else:
      print(f"没有写入权限: {file_path}")

  except Exception as e:
    print(f"发生错误: {e}")

# 获取软件的版本
def getSoftwareMD5():
  path = os.path.abspath(sys.argv[0])
  print(path)
  # 打开文件，并以二进制模式读取
  with open(path, 'rb') as f:
      # 创建一个md5对象
      md5 = hashlib.md5()
      
      # 逐块读取文件内容，并更新到md5对象中
      for chunk in iter(lambda: f.read(4096), b""):
          md5.update(chunk)
      
      # 返回计算出的md5哈希值
      return md5.hexdigest()

# 获取我的文档
def getDocPath(pathID=5):
  # 默认返回我的文档路径，出错时返回当前工作路径
  try:
    return shell.SHGetFolderPath(0, pathID, None, 0)
  except:
    return os.getcwd()

# 获取默认系统配置
def defaultSystemConfig(version):
  return {
    "version": version,
    "userPath": os.path.join(getDocPath(), "GreatNoteData", "user"),
    "tempPath": os.path.join(getDocPath(), "GreatNoteData", "temp"),
    "systemPath": os.path.join(getDocPath(), "GreatNoteData", "system"),
  }

# 获取平台信息
def platformInfo():
  # 获取操作系统名称
  os_name = platform.system()
  print("操作系统名称:", os_name)

  # 获取操作系统版本号
  os_version = platform.version()
  print("操作系统版本号:", os_version)

  # 获取操作系统发行版
  os_distribution = platform.uname()
  print("操作系统发行版:", os_distribution)

  # 获取计算机的网络名称
  network_name = platform.node()
  print("计算机的网络名称:", network_name)

  # 获取处理器信息
  processor_info = platform.processor()
  print("处理器信息:", processor_info)

  return {
    "os_name": os_name,
    "os_version": os_version,
    "os_distribution": os_distribution,
    "network_name": network_name,
    "processor_info": processor_info,
    "brief": f"{os_name},{os_version}"
  }