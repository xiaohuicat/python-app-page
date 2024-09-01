import os
from .LocalStore import LocalStore

# 高效参数存取模块
class Param(object):
  def __init__(self, filePath=None, default={}):
    self.filePath = filePath
    self.localStore = LocalStore(filePath) if filePath  else None
    self.count = 0
    self.default = default
    self.load()


  # 加载磁盘数据到内存
  def load(self):
    data = self.localStore.getAll() if self.localStore else {}
    if not data:
      self.count += 1
      self.data = self.default
    else:
      self.data = data
    return self.data


  # 判断参数中是否有数据
  def has(self, key:str):
    return key in self.data
  
  # 获取内存中的数据
  def get(self, key=None, default=None):
    # 如果没有指令，返回全部信息
    if not key and default == None:
      return self.data
    
    # 输入指令转化为参数列表
    attrList = key.split("/")
    # 参数列表倒置，从浅入深访问数据
    attrList.reverse()
    def extract(data):
      try:
        # 获取一层参数
        attr = attrList.pop(-1)
        # 尝试解释参数是否是数字，是就改为数字，不是就算了
        try:
          attr = int(attr)
        except:
          pass
        # 获取这层参数的值
        value = data[attr]
        # 如果参数列表还有参数，继续提取值，没有参数返回当前的值
        if len(attrList)>0:
          return extract(value)
        else:
          return value
      except:
        return default
    return extract(self.data)
    

  # 更新内存中的数据
  def update(self, key, value=None):
    self.count += 1
    if isinstance(key, list) or isinstance(key, dict):
      self.data = key
      return
    # 输入指令转化为参数列表
    attrList = key.split("/")
    # 参数列表倒置，从浅入深访问数据
    attrList.reverse()
    # 递归访问，直到找到输入指令所在位置的参数，并进行更新返回True，否则返回False
    def updateVal(data):
      try:
        # 获取一层参数
        attr = attrList.pop(-1)
        
        # 尝试解释参数是否是数字，是就改为数字，不是就算了
        isNum = False
        try:
          attr = int(attr)
          isNum = True
        except:
          pass

        # 如果参数列表还有参数，继续提取值，没有参数返回当前的值
        if len(attrList)>0:
          return updateVal(data[attr])
        # 如果参数列表没有参数了，赋值就好，但列表要存在能赋值
        else:
          # 如果参数是数字，判断数据是否是列表
          if isNum:
            if isinstance(data[attr], list) and len(data[attr])>= attr+1:
              data[attr] = value
              return True, "SUCCESS"
            else:
              return False, "NOT LIST"
          # 如果参数不是数字，直接赋值
          else:
            data[attr] = value
            return True, "SUCCESS"
      except:
        return False, "UPDATE FAIL"
    return updateVal(self.data)


  # 设置内存中的数据
  def set(self, key, value=None):
    self.count += 1
    if isinstance(key, list) or isinstance(key, dict):
      self.data = key
      return
    # 输入指令转化为参数列表
    attrList = key.split("/")
    # 参数列表倒置，从浅入深访问数据
    attrList.reverse()
    # 递归访问，直到找到输入指令所在位置的参数，并进行更新返回True，否则返回False
    def setVal(data):
      # 获取一层参数
      attr = attrList.pop(-1)

      # 如果参数能访问到数据，一直访问到最后一层，然后根据最后一层是什么数据执行相应的操作
      try:
        # 尝试解释参数是否是数字，是就改为数字，不是就算了
        isNum = False
        try:
          attr = int(attr)
          isNum = True
        except:
          pass

        # 如果参数列表还有参数，继续提取值，没有参数返回当前的值
        if len(attrList)>0:
          return setVal(data[attr])
        # 如果参数列表没有参数了，赋值就好，但列表要存在能赋值
        else:
          # 如果参数是数字，判断数据是否是列表
          if isNum:
            # 如果当前数据是列表，并且指定位置已存在数据，直接更换数据
            if isinstance(data, list) and len(data)>= attr+1:
              data[attr] = value
              return True, "SUCCESS"
            # 如果当前数据是列表，并且指定位置没有数据，保留原数据，分隔位置添加None子元素，指定位置放置指定数据
            elif isinstance(data, list) and len(data) < attr+1:
              for i in range(attr):
                try:
                  old = data[i]
                except:
                  old = None
                data[i] = old
              data[attr] = value
              return True, "SUCCESS"
            # 如果当前数据不是列表，创建一个空列表，在指定位置放置指定数据，其他位置设置为None
            else:
              return False, "NOT LIST"
          # 如果参数不是数字，直接赋值
          else:
            data[attr] = value
            return True, "SUCCESS"
      except:
        # 当前参数是数字
        isNum = False
        try:
          attr = int(attr)
          isNum = True
        except:
          pass
        # 如果参数列表还有值
        if len(attrList)>0:
          # 下一个参数是数字
          next_attr = attrList[-1] 
          nextIsNum = False
          try:
            next_attr = int(next_attr)
            nextIsNum = True
          except:
            pass
          
          _create = [] if nextIsNum else {}
          if isNum:
            # 如果data不是列表，则无法添加元素
            try:
              for i in range(attr):
                try:
                  data[i]
                except:
                  data.append(None)
              data.append(_create)
            except:
              return False, "NOT LIST"
          else:
            # 如果data不是对象，则无法添加元素
            try:
              data[attr] = _create
            except:
              return False, "NOT OBJECT"
          # 继续深挖
          if len(attrList)>0:
            return setVal(_create)
          return True, "SUCCESS"
        # 如果参数列表没有值了
        else:
          # 将指定值，赋值给当前参数
          if isNum:
            # 如果data不是列表，则无法添加元素
            try:
              for i in range(attr):
                try:
                  data[i]
                except:
                  data.append(None)
              data.append(value)
            except:
              return False, "NOT LIST"
          else:
            # 如果data不是对象，则无法添加元素
            try:
              data[attr] = value
            except:
              return False, "NOT OBJECT"
          return True, "SUCCESS"
    return setVal(self.data)
  

  # 保存内存的数据到磁盘
  def save(self, key=None, value=None):
    if isinstance(key, str):
      self.set(key,value)
      self.count += 1
    elif isinstance(key, list) or isinstance(key, dict):
      self.data = key
      self.count += 1
    
    if self.count > 0:
      # print(f">>>{self.filePath} save data:", self.data)
      self.localStore.save(self.data)
      self.count = 0
    else:
      pass
      # print(f">>>{self.filePath} save 数据未更改，无需保存")

  
  # 删除数据
  def delete(self, key, isSave=True):
    self.set(key, None)
    if isSave:
      self.save()
    

  # 读取数据并拼接路径
  def pathJoin(self, key, *args):
    return os.path.join(self.get(key), *args).replace("\\","/")
  
  
  # 清空内存中的数据
  def clear(self):
    self.data = None


  def child(self,path=None, default=None):
    return Param(path, default)
  

  def walk(self, pick=None, check=None, type="all", path=""):
    def func_all(data:list|dict, path:str, pick=None):
      if isinstance(data, list):
        for i in range(len(data)):
          pathList = [] if path == "" else path.split("/")
          pathList.append(str(i))
          func_all(data[i], "/".join(pathList), pick)
      elif isinstance(data, dict):
        check and check(path, data)
        for key in data.keys():
          pathList = [] if path == "" else path.split("/")
          pathList.append(key)
          func_all(data[key], "/".join(pathList), pick)
      else:
        pick and pick(path, data)

    def func_dict(data:dict, path:str, pick=None):
      if isinstance(data, dict):
        for key in data.keys():
          pathList = [] if path == "" else path.split("/")
          pathList.append(key)
          func_dict(data[key], "/".join(pathList), pick)
      else:
        pick and pick(path, data)
    
    if type == "all":
      func_all(data=self.data, path=path, pick=pick)
    elif type == "dict":
      func_dict(data=self.data, path=path, pick=pick)
    else:
      print("错误的类型")