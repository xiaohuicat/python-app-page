from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QLayout, QVBoxLayout, QHBoxLayout, QGridLayout
from app_page_core import Param, Page as CorePage
from ..core.Tips import Tips
from ..core.TipsBox import TipsBox
from ..core.PageManager import PageManager
from ..core.Thread import ThreadManager
from ..core.Setting import getSetting
from ..core.render import render
from ..core.WidgetsController import WidgetsController
from ..utils import layout_clear
from ..MainWindow import MainWindow


class Page(CorePage):
  def __init__(self, name=None) -> None:
    super().__init__(name)
    self.status:str
    self.app:QApplication
    self.root:Page
    self.mainWin:MainWindow
    self.pageManager:PageManager
    self.threadManager:ThreadManager
    self.param:Param
    self.localStore:Param
    self.pageParam:Param = Param()
    self.template:str
    self.playMedia:callable
    self.__widgetsController:WidgetsController = WidgetsController()
    self.__global_data:dict = {}
    self.__parent:QWidget|None = None
    self.__layout:QLayout|None = None
    # 判断是否挂载参数存储器
    if name and hasattr(self, "param"):
      path = self.param.pathJoin("userPath", f"pages/{name}/config.json")
      self.localStore = Param(path, {})
      if getSetting("IS_DEBUG"):
        print(f"页面 {name} 的本地存储路径为: {path}")


  def rerender(self, params:dict):
    if getSetting('IS_DEBUG'):
      print('[传递给模板的变量]', params)
    if not hasattr(self, 'template'):
      return
    self.hidePage()
    layout = self.getLayout()
    if not layout:
      self.setLayout('v-box')
      layout = self.getLayout()
    else:
      self.hidePage()
    
    layout.setAlignment(Qt.AlignTop)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(15)

    # 判断是否挂载layout容器
    if self.getLayout():
      self.hidePage()
    else:
      self.setLayout(layout)

    # 渲染页面并挂载组件id列表
    templateParams = params if type(params) == dict else {}
    renderResult = render(layout, self.template, templateParams)
    self.__widgetsController.setWidgets(renderResult['widgets'])
    self.__widgetsController.setWidgetList(renderResult['allWidgets'])


  def hidePage(self) -> None:
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
    self.pageParam and self.pageParam.clear()


  def destroy(self) -> None:
    def handle(*args):
      self.hidePage()
      self.status = 'hide'
      self.hide()
      self.__widgetsController = None
      if hasattr(self, "localStore"):
        self.localStore.clear()
        self.localStore = None
      self.pageParam = None
      self.children = None
      self.callback = None
      self.template = None
      self.__global_data = None
      self.__parent = None
    self.async_run(handle)


  # 注册事件
  def register(self, id:str, signal:str, callback) -> None:
    self.__widgetsController.register(id, signal, callback)


  # 导航到页面
  def navigateTo(self, id, *args) -> None:
    self.pageManager.open(*(id, *args))


  # 提示信息
  def tips(self, msg, type='default', pos=None, close=None) -> None:
    p = self.mainWin.win.window_position
    pos = [p[0]+p[2]/2, p[1]+p[3]/2]

    if hasattr(self.app, "tips_widget"):
      self.mainWin.win.mouseMoveEventHook.remove(id="tips")
      self.app.tips_widget.deleteLater()

    self.app.tips_widget = Tips(msg, type, pos)
    self.app.tips_widget.show()
    self.app.tips_widget.callback.add("close", close)

    def move_callback(pos) -> None:
      self.app.tips_widget.setPos([pos.x()+p[2]/2, pos.y()+p[3]/2])

    self.mainWin.win.mouseMoveEventHook.add(id="tips", func=move_callback)


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
    return self.__global_data.get(key, None) if type(key) == str else self.__global_data
  

  def setGlobal(self, key:str|dict, value:dict|None=None):
    if type(key) == str and value != None:
      self.__global_data[key] = value
    elif type(key) == dict and value == None:
      self.__global_data = key
    else:
      raise TypeError("参数错误，key必须为字符串且value不能为空，或key必须为字典且value必须为空")


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


  # 查看组件信息
  @property
  def info(self):
    return f"\n当前页面有{len(self.children.components.keys())}子页面。\n"+self.children.info()