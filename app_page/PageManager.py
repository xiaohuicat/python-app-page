from PySide6.QtWidgets import QWidget

class PageManager:
  def __init__(self):
    self.btn_dict = {}
    self.page_dict = {}
    self.data = {}

  # 添加栈
  def addStack(self, stack:QWidget):
    self.stack = stack

  # 添加页面
  def addPage(self, id:str|dict, Page=None):
    if isinstance(id,str):
      if Page:
        self.page_dict[id] = Page
    elif isinstance(id, dict):
      for each in id.keys():
        self.page_dict[each] = id[each]

  # 添加按钮参数
  def addButton(self, id:str, data:dict):
    if isinstance(id, str) and isinstance(data, dict):
      self.btn_dict[id] = data

  # 打开页面
  def open(self, id, *args):
    data = {}
    # 点击的页面立即展示
    if id in self.btn_dict:
      data["id"] = id
      # 跳转到页面
      param = self.btn_dict.get(id, None)
      index = param.get("stack_index", 0)
      self.stack.setCurrentIndex(index)
      print(f"*******显示{id}页面, index:", index)
      if id in self.page_dict:
        # 创建页面对象
        Page = self.page_dict[id]
        current = Page()                # 实例化页面
        current.setupPage()             # 初始化页面
        try:
          current["show"](param,*args)        # 展示页面
        except:
          try:
            current["show"](param)
          except:
            try:
              current["show"]()
            except Exception as e:
              print("===========> 显示页面报错:", e)
        data["current"] = current
      else:
        print("没有页面对象 id:", id)
    else:
      print("没有对应的页面 id:", id)
      
    # 刚才打开的页面将其隐藏
    if "current" in self.data and self.data["current"]:
      print(f"*******隐藏{self.data["id"]}页面")
      try:
        self.data["current"]["hide"](*args)
      except:
        try:
          self.data["current"]["hide"]()
        except Exception as e:
          print("===========> 隐藏页面报错:", e)
    # 将当前页面赋值
    if "id" in data:
      self.data["id"] = data["id"]
    if "current" in data:
      self.data["current"] = data["current"]

  # 销毁页面
  def destroy(self):
    self.page_dict = {}
    self.btn_dict = {}
    self.data = {}