from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout
from .render import render
from .Setting import getSetting
from ..utils import layout_clear


def UI_Render(target, stack:QWidget, template:str):
  layout = stack.layout()
  if not layout:
    layout = QVBoxLayout(stack)
  layout.setAlignment(Qt.AlignTop)
  layout.setContentsMargins(10, 10, 10, 10)
  layout.setSpacing(15)

  # 判断是否挂载layout容器
  if hasattr(target, "_render_root_layout"):
    UI_Remove(target)
  else:
    target._render_root_layout = layout
  
  # 渲染页面并挂载组件id列表
  target.widgetIdMap = render(layout, template)
  target.status = 'show'


def UI_Remove(target):
  # 如果存在删除挂载layout对象
  if hasattr(target, "_render_root_layout"):
    layout = target._render_root_layout
    layout_clear(layout)
    delattr(target, "_render_root_layout")
    
  # 如果存在持久化数据
  if hasattr(target, "localStore"):
    target.localStore.save()

  if hasattr(target, "widgetIdMap"):
    for key in target.widgetIdMap.keys():
      try:
        target.widgetIdMap[key].deleteLater()
        target.widgetIdMap[key] = None
      except:
        pass
    delattr(target, "widgetIdMap")
    
  target.status = 'hide'


def UI_Rerender(target, stack: QWidget, template:str):
  UI_Remove(target)
  UI_Render(target, stack, template)


class PageManager:
  def __init__(self):
    self.button_dict = {}
    self.page_dict = {}
    self.data = {}
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
    data = {}
    
    def create_page(param):
      # 创建页面对象
      Page = self.page_dict[id]
      # 实例化页面
      current = Page()
      # 添加全局数据
      if id in self.global_data:
        current.global_data = self.global_data[id]
      else:
        self.global_data[id] = {}
        current.global_data = self.global_data[id]
      # 初始化页面
      current.setup()
      data["current"] = current
      stack = self.stack.widget(index)
      rerender = lambda template: UI_Rerender(current, stack, template)
      current.rerender = rerender
      if hasattr(current, "template") and current.template:
        rerender(current.template)
      current.status = 'show'
      current.show(*({**param, "stack": stack}, *args)) # 展示页面
    
    def remove_page():
      last = self.data["current"]
      UI_Remove(last)
      last.global_data = None
      last.hide(*args)
    
    # 点击的页面立即展示
    if id in self.button_dict:
      data["id"] = id
      # 跳转到页面
      param = self.button_dict.get(id, None)
      index = param.get("stack_index", 0)
      self.stack.setCurrentIndex(index)
      if id in self.page_dict:
        if not getSetting("IS_DEBUG"):
          try:
            create_page(param)
          except Exception as error:
            print("打开页面出错：", error)
        else:
          create_page(param)

    # 刚才打开的页面将其隐藏
    if "current" in self.data and self.data["current"]:
      if not getSetting("IS_DEBUG"):
        try:
          remove_page()
        except Exception as error:
          print("隐藏页面出错：", error)
      else:
        remove_page()

    # 将当前页面赋值
    if id in self.button_dict:
      self.data["id"] = data["id"]
      self.data["current"] = data["current"]

  # 销毁页面
  def destroy(self):
    # 隐藏当前页面
    if "current" in self.data and self.data["current"]:
      try:
        current = self.data["current"]
        UI_Remove(current)
        current["hide"]()
      except Exception as e:
        print('销毁页面管理器报错：', e)
        pass
    self.page_dict = {}
    self.button_dict = {}
    self.data = {}