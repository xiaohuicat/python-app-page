import sys, time
from PySide6.QtCore import QThread, Signal

def default_fun(*args):
  # 此处调用函数
  print("6秒后返回数据")
  time.sleep(6)
  return {"data","测试数据"}

class EasyThread(QThread):
  response = Signal(object)
  def __init__(self, function=None):
    super().__init__()
    self.function = function if function else default_fun

  staticmethod
  def kill(self, Is_Wait=True):
    if Is_Wait:
      self.wait()
    else:
      self.quit()
    self.terminate()
    self.payload = None
    self.function = None
    self.response = None
    if self.isFinished():  # 如果线程还在运行
      del self

  def setPayload(self, payload):
    self.payload = payload

  def run(self):
    if hasattr(self, "payload"):
      ret = self.function(self.payload)
    else:
      ret = self.function()
    self.response and self.response.emit(ret)

class Waiting_time(EasyThread):
  def __init__(self,second):
    super().__init__()
    self.second = second

  def run(self):
    # print(f'即将在{self.second}s后尝试')
    time.sleep(self.second)
    self.response.emit(True)
   
class ThreadManager:
  def __init__(self):
    self.threadList = []

  # dict = {"thread", "function", "callback", "payload", "id"}
  def add(self, dict, isRun=False):
    thread = "thread" in dict and dict["thread"]
    func = "function" in dict and dict["function"]
    callback = "callback" in dict and dict["callback"]
    payload = "payload" in dict and dict["payload"]
    
    # 如果没有thread, 创建thread
    if not thread:
      thread = EasyThread(func)
      dict["thread"] = thread
    # 如果有payload，给thread设置payload
    if payload:
      thread.setPayload(payload)
    # 如有有callback，绑定返回信号给callback函数
    if callback:
      # print("绑定callback：", callback)
      thread.response.connect(callback)
    self.threadList.append(dict)
    isRun and thread.start()

  def run(self, id, payload=None):
    item = self.getOne(id)
    if item:
      if payload:
        # 如果有参数使用当前的参数
        item["thread"].setPayload(payload)
      else:
        # 如果没有参数使用初始化的参数
        if "payload" in item:
          item["thread"].setPayload(item["payload"])
      # 运行线程
      item["thread"].start()
    else:
      print("没有可用线程")

  def get(self, id):
    if hasattr(id, '__call__'):
      # 如果id是规则函数，直接传入
      return list(filter(id, self.threadList))
    elif isinstance(id, str):
      # 如果id是字符串，与每项的id进行比较
      return list(filter(lambda x:x.get("id")==id, self.threadList))

  def getOne(self, id):
    threadList = self.get(id)
    if len(threadList)>0:
      item = threadList.pop()
      return item
    else:
      return False

  def remove(self, id=None, param="SYSTEM"):
    if not id:
      threadList = self.threadList
      for each in threadList:
        print('移除线程：',each["id"] if "id" in each else "NULL", "  param:", param)
        thread = each["thread"]
        if hasattr(thread, "destroy"):
          try:
            thread.destroy(param)
          except Exception as e:
            print("============>关闭线程失败 e",e, "    id=", id)
        try:
          thread.response.disconnect()      # 解除信号与回调函数的连接
        except Exception as e:
          print("解除信号与槽的绑定失败 e:", e)
        if hasattr(thread, "ENABLE"):
          thread.kill(False)
        else:
          thread.kill()
        self.threadList = []
    else:
      threadList = self.get(id)
      for each in threadList:
        print('移除线程：', each["id"] if "id" in each else "NULL", "  param:", param)
        thread = each["thread"]
        if hasattr(thread, "destroy"):
          try:
            thread.destroy(param)
          except Exception as e:
            print("============>关闭线程失败 e",e, "    id=", id)
        try:
          thread.response.disconnect()      # 解除信号与回调函数的连接
        except Exception as e:
          print("解除信号与槽的绑定失败 e:", e)
        if hasattr(thread, "ENABLE"):
          thread.kill(False)
        else:
          thread.kill()
        self.threadList.remove(each)