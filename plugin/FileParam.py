import os, hashlib
from core.Param import Param

def md5_file(path):
# 打开文件，并以二进制模式读取
  with open(path, 'rb') as f:
      # 创建一个md5对象
      md5 = hashlib.md5()
      
      # 逐块读取文件内容，并更新到md5对象中
      for chunk in iter(lambda: f.read(4096), b""):
          md5.update(chunk)
      
      # 返回计算出的md5哈希值
      return md5.hexdigest()


class FileParam: 
  def __init__(self, filePath) -> None:
    self.filePath = os.path.abspath(filePath)
    self.param = Param(os.path.join(filePath, "info.json"))

  def info(self):
    total_size = 0
    for foldername, subfolders, filenames in os.walk(self.filePath):
      for filename in filenames:
        file_path = os.path.join(foldername, filename)
        md5 = md5_file(file_path)
        size = os.path.getsize(file_path)
        total_size += size
        dir_name = self.filePath.split("\\")[-1]
        ret_path = file_path.replace(self.filePath, dir_name).replace("\\","/")
        self.param.set(ret_path, [md5, size])
    
    return self.param.data
  

  def walk(self, callback=None):
    for foldername, subfolders, filenames in os.walk(self.filePath):
      for filename in filenames:
        file_path = os.path.join(foldername, filename)
        md5 = md5_file(file_path)
        size = os.path.getsize(file_path)
        dir_name = self.filePath.split("\\")[-1]
        ret_path = file_path.replace(self.filePath, dir_name).replace("\\","/")
        callback and callback({
          "ret_path": ret_path,
          "md5": md5,
          "size": size,
          "ext": os.path.splitext(filename)[1],
          "filename": filename
        })