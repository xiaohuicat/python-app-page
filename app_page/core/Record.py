# 记录管理器
class Record:
  def __init__(self, record_num=50) -> None:
    self.current_index = -1
    self.record_num = record_num
    self.record = []


  # 添加记录
  def addRecord(self, id):
    self.current_index = -1
    if len(self.record) >= self.record_num:
      self.record.pop(0)
    self.record.append(id)


  # 根据序号获取记录
  def getRecord(self, index=False):
    if index:
      return self.record[index]
    else:
      return self.record[-1]


  # 左侧记录
  def leftRecord(self):
    max = len(self.record) - 1
    if self.current_index == -1:
      self.current_index = max
    if self.current_index > 0:
      self.current_index = self.current_index - 1
    else:
      self.current_index = 0
    return False if self.current_index == -1 or len(self.record)==0 else self.record[self.current_index]


  # 右侧记录
  def rightRecord(self):
    max = len(self.record) - 1
    if self.current_index == -1:
      self.current_index = max
    if self.current_index < max:
      self.current_index = self.current_index + 1
    else:
      self.current_index = max
    return False if self.current_index == -1 else self.record[self.current_index]
