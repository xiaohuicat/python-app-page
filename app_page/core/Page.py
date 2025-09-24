import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QLayout, QVBoxLayout
from mako.template import Template
from app_page_core import Param, Page as CorePage
from ..core.Tips import Tips
from ..core.TipsBox import TipsBox
from ..core.PageManager import PageManager
from ..core.Thread import ThreadManager
from ..core.MainWindow import MainWindow
from ..core.Setting import getSetting
from ..core.render import render
from ..utils import layout_clear


class Page(CorePage):
  def __init__(self, name=None) -> None:
    super().__init__(name)
    self.status:str
    self.app:QApplication
    self.root:Page
    self.main_win:MainWindow
    self.ui:MainWindow.ui
    self.pageManager:PageManager
    self.threadManager:ThreadManager
    self.system_param:Param
    self.user_param:Param
    self.localStore:Param
    self.template:str
    self.__widgetIdMap:dict = {}
    self.__global_data:dict = {}
    self.__stack:QWidget|None = None
    self.__layout:QLayout|None = None
    # 判断是否挂载参数存储器
    if name and hasattr(self, "param"):
      path = self.param.pathJoin("userPath", f"pages/{name}/config.json")
      self.localStore = self.param.child(path, {})
      if getSetting("IS_DEBUG"):
        print(f"页面 {name} 的本地存储路径为: {path}")


  def setup(self, props=None) -> dict:
    super().setup(props)
    # 绑定函数
    if hasattr(self, "binds"):
      bind_dict = self.binds()
      for signal in bind_dict.keys():
        for [id, callback] in bind_dict[signal]:
          widget = self.ui[id]
          # 将对象的__dict__属性储存为一个字典
          widget_dict = widget.__dict__
          widget_dict[signal].connect(callback)
          disconnect = lambda args: lambda:args.disconnect()
          self.callback.add('onHide', disconnect(widget_dict[signal]))
    
    return {}
  

  def rerender(self, params:dict):
    self.status = 'show'
    if getSetting('IS_DEBUG'):
      print('[传递给模板的变量]', params)
    if not hasattr(self, 'template'):
      return
    self.hidePage()
    layout = self.__stack.layout()
    if not layout:
      layout = QVBoxLayout(self.__stack)
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
    self.setWidget(render(layout, Template(self.template).render(**templateParams)))


  def hidePage(self):
    # 移除组件映射
    for key in self.__widgetIdMap.keys():
      widget:QWidget = self.__widgetIdMap[key]
      widget.deleteLater()
    self.__widgetIdMap.clear()
    # 保存持久化数据
    if hasattr(self, "localStore"):
      self.localStore.save()
    # 移除挂载的元素
    if self.__layout:
      layout_clear(self.__layout)


  # 导航到页面
  def navigateTo(self, id, *args) -> None:
    self.pageManager.open(*(id, *args))


  # 提示信息
  def tips(self, msg, type='default', pos=None, close=None) -> None:
    p = self.main_win.move_win.window_position
    pos = [p[0]+p[2]/2, p[1]+p[3]/2]

    if hasattr(self.app, "tips_widget"):
      self.main_win.move_win.mouseMoveEventHook.remove(id="tips")
      self.app.tips_widget.deleteLater()

    self.app.tips_widget = Tips(msg, type, pos)
    self.app.tips_widget.show()
    self.app.tips_widget.callback.add("close", close)

    def move_callback(pos) -> None:
      self.app.tips_widget.setPos([pos.x()+p[2]/2, pos.y()+p[3]/2])

    self.main_win.move_win.mouseMoveEventHook.add(id="tips", func=move_callback)


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


  # 关闭页面
  def close(self) -> None:
    # 隐藏页面
    self.hidePage()
    # 销毁挂载的回调函数
    self.callback and self.callback.destroy()
    # 移除子组件
    self.children.remove()
    # 移除组件映射
    self.__widgetIdMap.clear()


  # 关闭app
  def closeApp(self) -> None:
    self.system_param.save()
    self.user_param.save()
    self.pageManager.destroy()
    self.threadManager.remove()
    self.children.remove()
    n = self.app.exec()
    try:
      sys.exit(n)
    except SystemExit:
      print('程序退出了，顺手帮你把垃圾带走')
      sys.exit(n)
  

  def setWidget(self, widgets:dict):
    self.__widgetIdMap = widgets


  def getWidget(self, id:str|None=None) -> QWidget|dict|None:
    return self.__widgetIdMap.get(id, None) if type(id) is str else self.__widgetIdMap


  def setStatus(self, status:str) -> None:
    self.status = status


  def getStatus(self) -> str:
    return self.status


  def hasGlobal(self, key:str) -> bool:
    return key in self.__global_data
  

  def getGlobal(self, key:str|None=None):
    return self.__global_data.get(key, None) if type(key) == str else self.__global_data
  

  def setGlobal(self, key:str|dict, value:dict|None=None):
    if type(key) == str and value != None:
      self.__global_data[key] = value
    else:
      self.__global_data = value
  

  def getStack(self) -> QWidget | None:
    return self.__stack


  def setStack(self, stack:QWidget):
    self.__stack = stack


  def getLayout(self) -> QLayout | None:
    return self.__layout


  def setLayout(self, layout:QLayout):
    self.__layout = layout

  
  # 查看组件信息
  @property
  def info(self):
    return f"\n当前页面有{len(self.children.components.keys())}子页面。\n"+self.children.info()