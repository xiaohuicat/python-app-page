import sys
from PySide6.QtWidgets import QApplication
from app_page_core import Page as CorePage
from app_page_core import Param
from ..core.Tips import Tips
from ..core.TipsBox import TipsBox
from ..core.PageManager import PageManager
from ..core.Thread import ThreadManager
from ..core.MainWindow import MainWindow

class Page(CorePage):
  def __init__(self, name=None):
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
    # 判断是否挂载参数存储器
    if name and hasattr(self, "param"):
      path = self.param.pathJoin("userPath", f"pages/{name}/config.json")
      print(f"当前页面name:{name} 配置文件path: {path}")
      self.localStore = self.param.child(path, {})
    self.widgetIdMap = {}

  def setup(self, props=None):
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

  # 导航到页面
  def navigateTo(self, id, *args):
    self.pageManager.open(*(id, *args))

  # 提示信息
  def tips(self, msg, type='default', pos=None, close=None):
    p = self.main_win.move_win.window_position
    pos=[p[0]+p[2]/2, p[1]+p[3]/2]

    if hasattr(self.app, "tips_widget"):
      self.main_win.move_win.mouseMoveEventHook.remove(id="tips")
      self.app.tips_widget.deleteLater()

    self.app.tips_widget = Tips(msg, type, pos)
    self.app.tips_widget.show()
    self.app.tips_widget.callback.add("close", close)

    def win_move(pos):
      self.app.tips_widget.setPos([pos.x()+p[2]/2, pos.y()+p[3]/2])

    self.main_win.move_win.mouseMoveEventHook.add(id="tips", func=win_move)

  # 提示窗
  def tipsBox(self, option, confirm=None, cancle=None, close=None):
    if hasattr(self, "_tips_box") and self._tips_box:
      print("请关闭后再打开")
      return
    self._tips_box = TipsBox(self.system_param, option)

    def _close():
      self._tips_box.callback.remove()
      self._tips_box.deleteLater()
      self._tips_box = None
      if callable(close): close()

    confirm and self._tips_box.callback.add("confirm", confirm)
    cancle and self._tips_box.callback.add("cancle", cancle)
    self._tips_box.callback.add("close", _close)
    self._tips_box.show()

  # 关闭页面
  def close(self):
    # 销毁挂载的回调函数
    self.callback and self.callback.destroy()
    # 移除子组件
    self.children.remove()
    # 移除组件映射
    self.widgetIdMap.clear()

  # 关闭app
  def closeApp(self):
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

  def getWidget(self, id:str|None):
    return self.widgetIdMap.get(id, None) if type(id) is str else self.widgetIdMap

  def setStatus(self, status:str):
    self.status = status

  def getStatus(self):
    return self.status

  # 查看组件信息
  @property
  def info(self):
    return f"\n当前页面有{len(self.children.components.keys())}子页面。\n"+self.children.info()