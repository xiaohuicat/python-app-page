# 记录管理器
class Record:
  def __init__(self, record_num:int=50) -> None:
    self.index = -1
    self.record_num = record_num
    self.record = []


  # 添加记录
  def addRecord(self, id:str):
    self.index = -1
    if len(self.record) >= self.record_num:
      self.record.pop(0)
    self.record.append(id)


  # 根据序号获取记录
  def getRecord(self, index=None):
    if index > -1:
      return self.record[index]
    else:
      return self.record[-1]


  # 左侧记录
  def leftRecord(self):
    max = len(self.record) - 1
    if self.index == -1:
      self.index = max
    if self.index > 0:
      self.index = self.index - 1
    else:
      self.index = 0
    return False if self.index == -1 or len(self.record)==0 else self.record[self.index]


  # 右侧记录
  def rightRecord(self):
    max = len(self.record) - 1
    if self.index == -1:
      self.index = max
    if self.index < max:
      self.index = self.index + 1
    else:
      self.index = max
    return False if self.index == -1 else self.record[self.index]
