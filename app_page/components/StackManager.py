import time
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from ..core import Record
from ..animation import RightClick_Menu
from .Stack import Stack
from ..utils import layout_clear


class StackManager(Stack):
  def __init__(self, options:dict):
    """初始化导航

    Args:
        options (dict): 控制参数
            stack_id (str): 栈的id
            filter_id (str): 过滤器id
            pageOptionList (list): 页面选项列表
            button_frame_id (str): 按钮容器的id
            button_container_id (str): 按钮容器的id
    """
    stack_id = options.get("stack_id", None)
    filter_id = options.get("filter_id", None)
    pageOptionList = options.get("pageOptionList", None)
    button_frame_id = options.get("button_frame_id", None)
    button_container_id = options.get("button_container_id", None)
    if not (stack_id and filter_id and pageOptionList and button_frame_id and button_container_id):
      raise Exception("StackManager初始化失败，options参数错误")

    super().__init__(id= stack_id)
    self.filter_id = filter_id
    self.record = Record()
    self.NOREPEAT = True      # 禁止重复
    self.DEBOUNCE = True      # 防抖开启
    self.DEBOUNCE_TIME = 200  # 200毫秒
    self.timestamp = 0
    self.current_btn = ""
    self.pageOptionList = pageOptionList if pageOptionList else []
    self.button_frame_id = button_frame_id
    self.button_container_id = button_container_id
    self._layout = None

  def setup(self):
    super().setup()
    self.button_frame:QFrame = self.ui[self.button_frame_id]
    self.button_container:QWidget = self.ui[self.button_container_id]
    self.createButton(self.pageOptionList)
    self.activeCurrentButton()


  def binds(self):
    return {
      "clicked": [
        ("btn_leftRecord", self.left_record),
        ("btn_rightRecord", self.right_record),
      ]
    }


  # 激活当前按钮
  def activeCurrentButton(self):
    current_id = self.system_param.get('leftBar_current_btn')
    if current_id:
      self.click(current_id, True)()
      return

    self.click(self.pageOptionList[0]["id"], True)()


  # 创建左侧导航栏按钮
  def createButton(self, pageOptionList:list):
    self.pageOptionList = [each for each in pageOptionList if each.get("filter", "") == self.filter_id]
    self.button_frame.setFixedHeight(360)
    layout = self.button_container.layout()
    if layout:
      self.deleteLeftbarButton(layout)
    else:
      layout = QVBoxLayout(self.button_container)
      layout.setAlignment(Qt.AlignTop)
    self._layout = layout
    # 增加新的元素
    for index, each in enumerate(self.pageOptionList):
      # 如果不存在对应的stack页面，创建一个空白的页面
      stack_id = each["stack_id"]
      stack_index = self.getIndexById(stack_id)
      each['stack_index'] = stack_index
      if stack_index == -1:
        stack = QWidget(self.button_frame)
        if "stack_id" in each:
          stack.setObjectName(stack_id)
        new_index = self.count()
        each['stack_index'] = new_index
        self.insertWidget(new_index, stack)

      button = QPushButton(each["name"], self.button_frame)
      button.setObjectName(each["id"])
      button.clicked.connect(self.click(each["id"]))
      button.setFixedHeight(40)

      # 添加右键菜单
      right_menu = []
      index != 0  and right_menu.append({
        "name": "上移",
        "icon": "./assets/icon/menu/up-arrow.png",
        "callback": self.refreshLeftBtn("up", each['id'])
      })
      index != len(self.pageOptionList)-1 and  right_menu.append({
        "name": "下移",
        "icon": "./assets/icon/menu/down-arrow.png",
        "callback": self.refreshLeftBtn("down", each['id'])
      })
      if "right_menu" in each:
        _right_menu = each["right_menu"]
        for e in _right_menu:
          right_menu.append({
            "name":e["name"],
            "icon":e["icon"],
            "callback":self.right_click(e["name"], each["id"])
          })
      RightClick_Menu(button, right_menu)
      # 添加到布局中
      layout.addWidget(button)


  def refreshLeftBtn(self, name, id):
    def fun():
      index = 0
      for each in self.pageOptionList:
        if each['id'] == id:
          break
        index += 1
      if name == "up":
        self.pageOptionList[index], self.pageOptionList[index-1] = self.pageOptionList[index-1], self.pageOptionList[index]
      elif name == "down":
        self.pageOptionList[index], self.pageOptionList[index+1] = self.pageOptionList[index+1], self.pageOptionList[index]
      
      layout_clear(self._layout)
      self.createButton(self.pageOptionList)
    return fun


  # 创建右侧导航栏按钮
  def deleteLeftbarButton(self, layout):
    count = layout.count()
    if layout is not None:
      for i in range(count):
        item = layout.takeAt(count - 1 - i)
        if not item:
          return
        widget = item.widget()
        if widget is not None:
          layout.removeWidget(widget)
          widget.deleteLater()


  # 设置当前激活按钮的样式
  def setActiveStyle(self, id, old_id:str):
    active_style = '#%s {background-color:rgba(0,0,0,0.04);font-weight:bold;font-size:18px}' % id
    styleSheetList = self.button_frame.styleSheet().split('\n')
    # 删除旧的值
    if old_id and styleSheetList[-1].find(f'#{old_id}') > -1:
      styleSheetList.pop()
    styleSheetList.append(active_style)
    # 将新的样式表设置到程序中
    self.button_frame.setStyleSheet('\n'.join(styleSheetList))


  # 点击事件，根据名称打开对应的页面
  def click(self, id, isActive=None):
    def fun(NO_RECORD=False):
      # 判断重复点击
      if not isActive and self.NOREPEAT and self.current_btn == id:
        self.tips("重复点击")
        return
      # 设置防抖
      current = int(time.perf_counter() * 1000)
      if not isActive and self.DEBOUNCE:
        if (current - self.timestamp) < self.DEBOUNCE_TIME:
          self.tips("过于频繁")
          return

      dataList = list(filter(lambda x:x.get("id")==id, self.pageOptionList))
      if len(dataList) > 0:
        index = self.getIndexById(dataList[0]["stack_id"])
        index = index if index != -1 else 0
      else:
        index = 0
      self.setCurrentPage(index)
      self.setActiveStyle(id, old_id=self.current_btn)

      # 保存记录
      if not NO_RECORD:
        self.record.addRecord(id)

      self.current_btn = id
      self.timestamp = current
      self.system_param.set('leftBar_current_btn', id)
      self.navigateTo(id)

    return fun


  def right_click(self, id, page_name):
    return lambda :self.callback.run("right_click", page_name, id)


  def left_record(self):
    id = self.record.leftRecord()
    if id:
      self.click(id)(True) # 不记录


  def right_record(self):
    id = self.record.rightRecord()
    if id:
      self.click(id)(True) # 不记录