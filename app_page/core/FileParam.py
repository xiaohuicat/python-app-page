import os, hashlib
from app_page_core import Param

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
    
    # size_mb = total_size/1024/1024
    # print(f"fileSize={size_mb:.3f}Mb")
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
    

  def update(self):
    # self._size = 0
    # zip = ZIP()
    # zip.setMode("7z")
    # def download(path, value):
    #   _dir_name, full_file_name = os.path.split(path)
    #   dir_name = _dir_name.replace("dist","zip")
    #   file_name, file_ext = os.path.splitext(full_file_name)
    #   dist_path = os.path.join(dir_name, file_name+"."+zip.mode)
    #   if not os.path.exists(dir_name):
    #     os.makedirs(dir_name)
    #   if zip.zip_file(path, dist_path):
    #     print("压缩成功...")
    #   else:
    #     print("压缩失败...")

    #   # if md5_file(path) == value[0]:
    #   #   # print("path:", path, value[0])
    #   #   print("文件已存在")
    #   # else:
    #   #   print("正在下载 path:", path, value[0])
    #   #   self._size += value[1]

    # self.param.walk(pick=download, type="dict", path="dist/main")
    # size_kb = self._size/1024
    # print(f"下载的文件大小{size_kb:.3f}kb")
    pass