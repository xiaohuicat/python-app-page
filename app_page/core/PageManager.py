from PySide6.QtWidgets import QStackedWidget
from .Setting import getSetting
from .callfunc import call_func

GLOBAL_DESTROY_KEY = '__destroy'

class PageManager:
  def __init__(self):
    self.current_id = None
    self.current_page = None
    self.stack = None
    self.data = {}
    self.page_dict = {}
    self.button_dict = {}
    self.global_data = {}


  def mount(self, stackedWidget:QStackedWidget, pages:dict, pageOptionList:list):
    """
    挂载页面管理器

    Args:
        stackedWidget (QStackedWidget): 栈组件
        pages (dict): 页面字典，{页面id:页面对象}
        pageOptionList (list): 页面参数列表 
    """
    # 添加栈
    self.addStack(stackedWidget)
    # 添加页面
    for key in pages.keys():
      value = pages[key]
      self.addPage(key, value)
    # 添加按钮
    for each in pageOptionList:
      key = each.get("id", None)
      if key:
        self.addButton(key, each)


  # 添加栈
  def addStack(self, stack):
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
      self.button_dict[id] = data


  # 打开页面
  def open(self, id, *args):
    temp_dict = {}
    
    def create_page(param, stack):
      # 创建页面对象
      Page = self.page_dict[id]
      # 实例化页面
      current = Page()
      # 添加全局数据
      if id not in self.global_data:
        self.global_data[id] = {}
      current.setGlobal(self.global_data[id])
      # 初始化并获取初始化参数
      if getSetting('SETUP_EASY'):
        params = call_func(current.setup)
        del params['self']
      else:
        params = current.setup()
      temp_dict["current"] = current
      current.setParent(stack)
      if params:
        current.rerender(params)
      current.status = 'show'
      current.show(*{*args, *param})
    
    def remove_page():
      last = self.current_page
      last.destroy()
    
        # 刚才打开的页面将其隐藏
    
    # 隐藏当前页面
    if self.current_page:
      if not getSetting("IS_DEBUG"):
        try:
          remove_page()
        except Exception as error:
          print("隐藏页面出错：", error)
      else:
        remove_page()
    
    # 展示点击的页面
    if id in self.button_dict:
      temp_dict["id"] = id
      # 跳转到页面
      param = self.button_dict.get(id, None)
      index = param.get("stack_index", 0)
      self.stack.setCurrentIndex(index)
      stack = self.stack.widget(index)
      if id in self.page_dict:
        if not getSetting("IS_DEBUG"):
          try:
            create_page(param, stack)
          except Exception as error:
            print("打开页面出错：", error)
            return
        else:
          create_page(param, stack)

    # 将当前页面赋值
    if id in self.button_dict:
      self.current_id = temp_dict["id"]
      self.current_page = temp_dict["current"]


  # 销毁页面
  def destroy(self):
    # 检查global_data是否存在需要保存的东西
    for key in self.global_data.keys():
      each = self.global_data[key]
      if GLOBAL_DESTROY_KEY in each and callable(each[GLOBAL_DESTROY_KEY]):
        each[GLOBAL_DESTROY_KEY]()
    # 销毁当前页面
    if self.current_page:
      try:
        self.current_page.destroy()
      except Exception as e:
        print('销毁页面管理器报错：', e)
        pass
    # 清除数据
    self.page_dict = {}
    self.button_dict = {}
    self.global_data = {}
    self.current_id = None
    self.current_page = None
    self.stack = None