import hashlib

def md5_text(text):
  # 创建一个md5对象
  m = hashlib.md5()
  # 向md5对象中提供要哈希的文本（需要将其转换为字节对象）
  m.update(text.encode('utf-8'))
  # 获取哈希值并以16进制字符串的形式返回
  return m.hexdigest()

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