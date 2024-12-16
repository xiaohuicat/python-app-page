import time, os
from nanoid import generate
from .Store import Store
from .Callback import Callback
from .Children import Children
from .Param import Param

class Page:
  def __init__(self, name=None):
    self.name = name
    self.id = generate(size=10)
    self.callback = Callback()                     # 挂载回调函数管理对象
    self.children = Children()                     # 挂载子页面管理对象
    self.store = Store()                           # 挂载全局变量管理对象
    self.props:Param
    self.events:Param
    self.onShow = None
    self.onHide = None

  # 页面初始化
  def setup(self, props=None):
    """
    1.加载和设置页面参数
    2.挂载子页面
    3.添加回调函数
    4.绑定事件
    """
    # 加载和设置页面参数
    loadProps(self, props)
    self.name = self.props.get('name', self.name)
    self.id = self.props.get('id', self.id)
    self.events = Param(default=self.props.get('events')) if self.props.has('events') else Param()
    # 挂载子页面
    self.children.setup(self.props.get('children'), createPage)
    # 添加回到函数
    addCallback(self, self.props.get('functions', {}))
    # 绑定事件
    executeBinds(self)
    # print(f'页面[{self.name}]{self.id}初始化完成 props:{self.props.get()}')
  
  def bind(self, signal:str, id:str, func:callable):
    self.events.set(f'{signal}/{id}', func)
    executeBind(self, signal, id, func)
    
  # 关闭页面
  def close(self):
    self.children.close()

  # 展示页面
  def show(self, *args):
    if type(self.onShow, callable):
      self.onShow(*args)

  # 隐藏页面
  def hide(self, *args):
    if type(self.onHide, callable):
      self.onHide(*args)

  def wait(self, second, callback):
    threadManager = self.store.get('threadManager', None)
    if not threadManager:
      return
    
    id = f"wait_{generate(size=6)}_{time.time()*1000}"
    def func(*args, **kwargs):
      try:
        callback(*args, **kwargs)
      except Exception as e:
        print("等待回调失败：", e)
      threadManager.remove(id)
      
    threadManager.add({
      "id": id,
      "callback": func,
      "function": lambda: time.sleep(second)
    }, True)

  def async_run(self, function, callback):
    threadManager = self.store.get('threadManager', None)
    if not threadManager:
      return
        
    id = f"async_run_{generate(size=6)}_{time.time()*1000}"
    def func(*args, **kwargs):
      try:
        callback(*args, **kwargs)
      except Exception as e:
        print("异步回调失败：", e)
      threadManager.remove(id)
    
    threadManager.add({
      "id": id,
      "callback": func,
      "function": function
    }, True)

  def call(self, name:str, *args):
    def run():
      self.callback.run(name, *args)
    return run

  # 查看组件信息
  @property
  def info(self):
    info_string = f"\n当前页面[{self.name}]有{len(self.children.components.keys())}子页面。\n"+self.children.info()
    return info_string

  def __getitem__(self, __name):
    return super().__getattribute__(__name)
  
  def __getattribute__(self, __name):
    if self["store"].has(__name):
      return self["store"].get(__name)
    else:
      return super().__getattribute__(__name)

# 创建页面
def createPage(name:str):
  return Page(name)

# 加载属性
def loadProps(self:Page, props:any):
  if type(props) == str and os.path.exists(props):
    self.props = Param(filePath=props)
  elif type(props) == dict:
    self.props = Param(default=props)
  elif type(props) == Param:
    self.props = props
  else:
    self.props = Param()

# 执行绑定列表
def executeBinds(page:Page):
  dataList = page.events.data
  for signal in dataList.keys():
    idDict = dataList[signal]
    if type(idDict) == dict:
      for id in idDict.keys():
        slot = page.events.data[signal][id]
        executeBind(page, signal, id, slot)

# 执行绑定
def executeBind(page:Page, signal:str, id:str, slot):
  functions = page.store.get('functions')
  if type(functions) == dict and '__signal_slots_func' in functions:
    __signal_slots_func = functions['__signal_slots_func']
    if hasattr(__signal_slots_func, '__call__'):
      if type(slot) == str:
        def call(name:str):
          return lambda *args: page.callback.run(name, *args)
      # 执行绑定函数
      __signal_slots_func(signal, id, call(slot))

# 添加回调函数      
def addCallback(page:Page, functions:dict):
  for name in functions.keys():
    def generate(pycode):
      if type(pycode) == str and os.path.exists(pycode):
        with open(pycode, 'r', encoding='utf-8') as f:
          pycode = f.read()
      elif type(pycode) == str:
        pass
      else:
        pycode = 'print("['+name+']未找到回调函数")'
      return lambda *args: exec(pycode, {"page":page, "args":args})
    # 添加到回调管理器
    page.callback.add(name, generate(functions[name]))