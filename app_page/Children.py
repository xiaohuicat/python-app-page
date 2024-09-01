import os
from .Param import Param

class Children(object):
  def __init__(self):
    self.components = dict()
    self.props:Param
  # 查看当前页面的子页面信息
  def info(self, level="——"):
    info_string = ""
    for key in self.components.keys():
      info_string += level + key + "\n"
      info_string += self.components.get(key).children.info(level="  "+level)
    return info_string

  # 子页面初始化
  def setup(self, props=None, createPage=None):
    loadProps(self, props)
    # 初始化存在的页面
    keys =  list(self.components.keys())
    for key in keys:
      component = self.components[key]
      if hasattr(component, 'setup'):
        if self.props.has(component.name):
          component.setup(self.props.get(component.name))
        else:
          component.setup()
    # 初始化缺失的页面    
    props = self.props.get()
    children = props.keys()
    for child in children:
      if child not in self.components.keys():
        component = createPage(child)
        self.components[child] = component
        component.setup(self.props.get(child))

  # 添加子页面
  def add(self, name:str, component:object):
    if name not in self.components.keys():
      self.components[name] = component
    else:
      AttributeError(name=f"{name}组件已存在")

  # 获取子页面
  def get(self, name:str):
    if name in self.components.keys():
      return self.components[name]
    else:
      return None
    
  def has(self, name:str):
    return name in self.components.keys()
  
  # 显示组件
  def show(self, name):
    if (type(name).__name__=='list'):
      for each in name:
        self.components[each].show()
    else:
      self.components[each].show()

  # 隐藏组件
  def hide(self, name):
    if (type(name).__name__=='list'):
      for each in name:
        self.components[each].hide()
    else:
      self.components[each].hide()

  # 关闭组件
  def close(self, name):
    if (type(name).__name__=='list'):
      for each in name:
        self.components[each].close()
    else:
      self.components[each].close()

  # 移除组件
  def remove(self, name=None):
    if not name:
      for each in self.components.values():
        if hasattr(each, "destroy"):
          each.destroy()
        each.children.remove()  # 移除子组件的子组件
        self.components = {}
    else:
      if name in self.components.keys():
        each = self.components[name]
        each.children.remove() # 移除子组件的子组件
        if hasattr(each, "destroy"):
          each.destroy()        
        del each

  def __getitem__(self, __name):
    if __name in self.components.keys():
      return self.components[__name]
    else:
      print(self.components)
      return None
    
# 加载属性
def loadProps(self:object, props:any):
  if type(props) == str and os.path.exists(props):
    # 检查文件是被存在循环引用
    self.props = Param(filePath=props)
  elif type(props) == dict:
    self.props = Param(default=props)
  elif type(props) == Param:
    self.props = props
  else:
    self.props = Param()