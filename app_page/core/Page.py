import time
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QLayout, QVBoxLayout, QHBoxLayout, QGridLayout
from app_page_core import Callback, Children, Param, Store
from nanoid import generate
from ..core.Tips import Tips
from ..core.TipsBox import TipsBox
from ..core.PageManager import PageManager
from ..core.Thread import ThreadManager
from ..core.Setting import getSetting
from ..core.render import render
from ..core.WidgetsController import WidgetsController
from ..utils import layout_clear, blur_image
from ..MainWindow import MainWindow


class Page:
  def __init__(self, name=None) -> None:
    self.name = name
    self.id = generate(size=10)
    self.callback = Callback()                     # 挂载回调函数管理对象
    self.children = Children()
    self.store:Store = Store()
    self.status:str = 'hide'

    self.app:QApplication
    self.root:Page
    self.mainWin:MainWindow
    self.pageManager:PageManager
    self.threadManager:ThreadManager
    self.param:Param
    self.localStore:Param
    self.pageParam:Param = Param()

    self.template:str = "<template></template>"
    self.style:str = ""
    self.playMedia:callable
    self.__widgetsController:WidgetsController = WidgetsController()
    self.__global_data:dict = {}
    self.__parent:QWidget|None = None
    self.__layout:QLayout|None = None
    # 判断是否挂载参数存储器
    if name:
      path = self.getSoftwarePath("userPath", f"pages/{name}/config.json")
      self.localStore = Param(path, {})
      if getSetting("IS_DEBUG"):
        print(f"页面 {name} 的本地存储路径为: {path}")

  
  def setup(self) -> dict|None:
    return None


  def rerender(self, params:dict):
    if getSetting('IS_DEBUG'):
      print('[传递给模板的变量]', params)
    if not hasattr(self, 'template'):
      return
    self.hideBefore()
    layout = self.getLayout()
    if not layout:
      self.setLayout('v-box')
      layout = self.getLayout()
    else:
      self.hideBefore()
    
    layout.setAlignment(Qt.AlignTop)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(15)
    if self.style:
      self.getParent().setStyleSheet(self.style)

    # 判断是否挂载layout容器
    if self.getLayout():
      self.hideBefore()
    else:
      self.setLayout(layout)

    # 渲染页面并挂载组件id列表
    templateParams = params if type(params) == dict else {}
    renderResult = render(layout, self.template, templateParams)
    self.__widgetsController.setWidgets(renderResult['widgets'])
    self.__widgetsController.setWidgetList(renderResult['allWidgets'])


  def show(self, *args) -> None:
    print("显示页面:", self.name or self.id, "参数:", args)


  def hide(self, *args) -> None:
    print("隐藏页面:", self.name or self.id, "参数:", args)


  def hideBefore(self) -> None:
    if self.__layout:
      layout_clear(self.__layout)
      self.__layout = None
    # 销毁组件管理器
    if self.__widgetsController:
      self.__widgetsController.destroy()
    if self.children:
      self.children.remove()
    if self.callback:
      self.callback.clear()
    # 保存持久化数据
    if hasattr(self, "localStore"):
      self.localStore.save()


  def destroy(self) -> None:
    self.hideBefore()
    self.status = 'hide'
    try:
      self.hide()
    except Exception as e:
      print("页面隐藏时出错：", e)
    self.__widgetsController = None
    if hasattr(self, "localStore"):
      self.localStore.clear()
      self.localStore = None
    app_callback:Callback = self.store.get('APP_CALLBACK')
    app_callback.remove('event-filter')
    self.pageParam and self.pageParam.clear()
    self.pageParam = None
    self.children = None
    self.callback = None
    self.template = None
    self.__parent = None


  # 注册事件
  def register(self, id:str, signal:str, callback) -> None:
    self.__widgetsController.register(id, signal, callback)
    
    
  def regist_filter(self, callback):
    app_callback:Callback = self.store.get('APP_CALLBACK')
    app_callback.remove('event-filter')
    app_callback.add('event-filter', callback)


  # 导航到页面
  def navigateTo(self, id, *args) -> None:
    self.pageManager.open(*(id, *args))


  # 设置定时器
  def setTimeout(self, callback, seconds:float):
    if not self.threadManager:
      return
    
    thread_id = f"wait_{generate(size=6)}_{time.time()*1000}"
    def func(*args, **kwargs):
      try:
        callback(*args, **kwargs)
      except Exception as e:
        print("等待回调失败：", e)
      self.threadManager.remove(thread_id)

    self.threadManager.add({
      "id": thread_id,
      "callback": func,
      "function": lambda: time.sleep(seconds)
    }, True)

    return thread_id
  

  # 清除定时器
  def clearTimeout(self, thread_id):
    if not self.threadManager:
      return
    self.threadManager.remove(thread_id)


  # 异步执行函数
  def async_run(self, function, callback=None):
    if not self.threadManager:
      return

    thread_id = f"async_run_{generate(size=6)}_{time.time()*1000}"
    def func(*args, **kwargs):
      try:
        callback(*args, **kwargs)
      except Exception as e:
        print("异步回调失败：", e)
      self.threadManager.remove(thread_id)
    
    self.threadManager.add({
      "id": thread_id,
      "callback": func,
      "function": function
    }, True)


  # 提示信息
  def tips(self, msg, type='default') -> None:
    hook = self.mainWin.win.mouseMoveEventHook
    if hasattr(self.app, "tips_widget"):
      hook.remove(id="tips")
      self.app.tips_widget.deleteLater()

    self.app.tips_widget = Tips(msg, type)
    hook.add(id="tips", func=lambda *args: self.app.tips_widget.center())


  # 提示窗
  def tipsBox(self, topic='', title='', content='', confirm=None, cancle=None, close=None) -> None:
    if hasattr(self, "_tips_box") and self._tips_box:
      print("请关闭后再打开")
      return
    self._tips_box = TipsBox(topic=topic, title=title, content=content)

    def _close() -> None:
      self._tips_box.callback.remove()
      self._tips_box.deleteLater()
      self._tips_box = None
      if callable(close): close()

    confirm and self._tips_box.callback.add("confirm", confirm)
    cancle and self._tips_box.callback.add("cancle", cancle)
    self._tips_box.callback.add("close", _close)
    self._tips_box.show()
  

  def setWidgets(self, widgets:dict):
    self.__widgetsController.setWidgets(widgets)


  def getWidget(self, id:str|None=None) -> QWidget|dict|None:
    return self.__widgetsController.getWidget(id)


  def setStatus(self, status:str) -> None:
    self.status = status


  def getStatus(self) -> str:
    return self.status


  def hasGlobal(self, key:str) -> bool:
    return self.__global_data and key in self.__global_data
  

  def getGlobal(self, key:str|None=None):
    return self.__global_data.get(key, None) if self.__global_data and type(key) == str else self.__global_data
  

  def setGlobal(self, key:str|dict, value:dict|None=None):
    if type(key) == str and value != None:
      self.__global_data[key] = value
    elif type(key) == dict and value == None:
      self.__global_data = key
    else:
      raise TypeError("参数错误，key必须为字符串且value不能为空，或key必须为字典且value必须为空")


  def onGlobalDestroy(self, callback:callable) -> None:
    self.setGlobal('__destroy', callback)


  def getParent(self) -> QWidget | None:
    return self.__parent


  def setParent(self, parent:QWidget=None) -> None:
    if not parent:
      self.__parent = QWidget()
      return
    self.__parent = parent


  def getLayout(self) -> QLayout | None:
    if not self.__layout:
      self.__layout = self.__parent.layout() if self.__parent else None
    return self.__layout


  def setLayout(self, layoutType:str):
    if not isinstance(self.__parent, object):
      raise ValueError("请先设置父组件")
    if layoutType == 'v-box':
      self.__layout = QVBoxLayout(self.__parent)
    elif layoutType == 'h-box':
      self.__layout = QHBoxLayout(self.__parent)
    elif layoutType == 'grid':
      self.__layout = QGridLayout(self.__parent)
    else:
      raise ValueError("不支持的布局类型, 请使用 'v-box', 'h-box', 'grid' 之一")


  def getSoftwarePath(self, typeName: str, *args):
    if typeName not in ['userPath', 'tempPath', 'systemPath']:
      raise ValueError(f"typeName: {typeName} 不在允许的列表['userPath', 'tempPath', 'systemPath']中")
    return self.param.pathJoin(typeName, *args)


  def getBlurImage(self, url: str, radius: float = 5, opacity: float = 1):
    folder = self.getSoftwarePath("tempPath", "blur_images")
    return blur_image(folder, url, radius, opacity)


  # 查看组件信息
  @property
  def info(self):
    return f"\n当前页面有{len(self.children.components.keys())}子页面。\n"+self.children.info()


  def __getitem__(self, __name):
    return super().__getattribute__(__name)


  def __getattribute__(self, __name):
    if self["store"].has(__name):
      return self["store"].get(__name)
    else:
      return super().__getattribute__(__name)