import py7zr
import os
import tempfile
import shutil


def zip_file(file_path, zip_path):
  try:
    with py7zr.SevenZipFile(zip_path, 'w') as zip_file:
      # 添加文件到压缩文件中
      zip_file.write(file_path, os.path.basename(file_path))
    return True
  except Exception as e:
    print(e)
    return False
    

def zip_files(file_paths, zip_path):
  try:
    with py7zr.SevenZipFile(zip_path, 'w') as zip_file:
      for file_path in file_paths:
        # 将文件添加到压缩文件中，第二个参数是压缩包中的文件名
        zip_file.write(file_path, os.path.basename(file_path))
    return True
  except Exception as e:
    print(e)
    return False


def zip_foder(foder_path, zip_path):
  try:
    with py7zr.SevenZipFile(zip_path, 'w') as zip_file:
      for root, dirs, files in os.walk(foder_path):
        for file in files:
            file_path = os.path.join(root, file)
            zip_file.write(file_path, os.path.relpath(file_path, os.path.join(foder_path, '..')))
    return True
  except:
    return False


def unzip_file(zip_file_path, extract_folder):
    with tempfile.TemporaryDirectory() as temp_dir:
      try:      
          fz = py7zr.SevenZipFile(zip_file_path, 'r')
          for file in fz.namelist():
              fz.extract(file, temp_dir)

          # 复制解压后的文件到目标文件夹
          for root, dirs, files in os.walk(temp_dir):
              for file in files:
                  source_path = os.path.join(root, file)
                  destination_path = os.path.join(extract_folder, file)

                  # 确保目标文件夹存在
                  os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                  # 复制文件
                  shutil.copy(source_path, destination_path)
          return True
      except Exception as e:
          print("解压失败 e",e)
          return False 

