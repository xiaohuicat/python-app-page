import sys
from app_page_core import Page as CorePage
from ..core.Tips import Tips
from ..core.TipsBox import TipsBox

class Page(CorePage):
  def __init__(self, name=None):
    super().__init__(name)

  # 挂载子页面
  def mount(self, pageDict:dict, btnList:list):
    # 添加栈
    self.page_manager.add_stack(self.ui.stackedWidget)
    # 添加页面
    for key in pageDict.keys():
      value = pageDict[key]
      self.page_manager.add_page(key, value)
    # 添加按钮
    for each in btnList:
      key = each.get("id", None)
      if key:
        self.page_manager.add_btn(key, each)

  # 导航到页面
  def navigateTo(self, id, param=None):
    if param:
      self.page_manager.open(id, param)
    else:
      self.page_manager.open(id)

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
    if hasattr(self, "tips_box") and self.tips_box:
      print("请关闭后再打开")
      return
    self.tips_box = TipsBox(self.system_param, option)

    def _close():
      self.tips_box.callback.remove()
      self.tips_box.deleteLater()
      self.tips_box = None
      close and close()

    confirm and self.tips_box.callback.add("confirm", confirm)
    cancle and self.tips_box.callback.add("cancle", cancle)
    self.tips_box.callback.add("close", _close)
    self.tips_box.show()

  # 关闭页面
  def close(self):
    # 销毁挂载的回调函数
    self.callback and self.callback.destroy()
    # 移除子组件
    self.children.remove()

  # 页面初始化
  def init_page(self):
    # 页面初始化
    if hasattr(self, 'setup'):
      self.setup()
    
    # 绑定函数
    if hasattr(self, "binds"):
      bind_dict = self.binds()
      for signal in bind_dict.keys():
        for each in bind_dict[signal]:
          self.ui[each[0]][signal].connect(each[1])

  # 关闭app
  def closeApp(self):
    self.system_param.save()
    self.user_param.save()
    self.thread_manager.remove()
    self.children.remove()
    n = self.app.exec()
    try:
      sys.exit(n)
    except SystemExit:
      print('程序退出了，顺手帮你把垃圾带走')
      sys.exit(n)
      
  # 查看组件信息
  @property
  def info(self):
    info_string = f"\n当前页面有{len(self.children.components.keys())}子页面。\n"+self.children.info()
    return info_string