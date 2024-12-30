import utils.ZIP.File7Zip as File7Zip
import utils.ZIP.FileZip as FileZip

class ZIP:
  def __init__(self):
    self.mode = "zip"
    self.engine = FileZip

  def setMode(self, mode="zip"):
    self.mode = mode
    if mode == "zip":
      self.engine = FileZip
    elif mode == "7z":
      self.engine = File7Zip
    else:
      print("错误的压缩模式")

  def zip_file(self, file_path, zip_path):
    return self.engine.zip_file(file_path, zip_path)
  
  def zip_files(self, file_paths, zip_path):
    return self.engine.zip_files(file_paths, zip_path)
  
  def zip_foder(self, foder_path, zip_path):
    return self.engine.zip_foder(foder_path, zip_path)
  
  def unzip_file(self, zip_file_path, extract_folder):
    return self.engine.unzip_file(zip_file_path, extract_folder)