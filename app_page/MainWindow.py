import os
from PySide6.QtWidgets import QMainWindow, QWidget, QLayout
from PySide6 import QtCore
from app_page_core import Param, Callback
from .core.render.render_main import render
from .core.WidgetsController import WidgetsController
from .core.Setting import getSetting
from .animation import MoveWin
from .config import Config
from .utils import assetsUrl, setShadowEffect, assetsRead, s2t


template = '''
<template>
  <div id="main-ui" class="main-container" width="1080" height="745">
    <v-box margins="[0,0,0,0]" spacing="0">
      <div id="app_header" class="header" height="50">
        <h-box spacing="0" margins="[15,0,15,0]">
          <label id="app_name" text="${title}"/>

          <!-- 用户登录信息 -->
          <div height="50" width="260" margins="[0,0,30,0]">
            <h-box margins="[0,0,0,0]" spacing="6">
              <div />
              <button id="btn_login_icon" width="32" height="32" />
              <button id="btn_login_text" text="请登录" width="55" height="28"/>
              <button id="btn_skin" width="28" height="28" />
              <button id="btn_setting" width="28" height="28" />
              <button id="btn_message" width="28" height="28" />
            </h-box>
          </div>

          <!-- 窗口操控栏 -->
          <div height="50" width="115">
            <h-box margins="[0,0,0,0]" spacing="10">
              <div />
              <button id="btn_change" height="28" width="28"/>
              <button id="btn_small" height="28" width="28"/>
              <button id="btn_close" height="28" width="28"/>
            </h-box>
          </div>
        </h-box>
      </div>
      <div id="app_main" class="main">
        <h-box margins="[0,0,0,0]" spacing="0">
          <div class="left-bar" id="leftbar_container" width="200">
          </div>
          <div class="content">
            <v-box margins="[0,0,0,0]" spacing="10">
              <QStackedWidget id="stackedWidget" />
            </v-box>
          </div>
        </h-box>
      </div>
    </v-box>
  </div>
</template>
'''

main_window_style = lambda:'''
/* 顶部栏样式 */
.header {
  background-color: #2165A9;
}
#app_name {
  color: #fff;
  font-size: 22px;
  font-weight: bold;
}
#btn_login_icon {
  border-radius: 16px;
  background-color: transparent;
}
#btn_login_text {
  color: #fff;
  font-size: 14px;
  border-radius: 6px;
  background-color: transparent;
}
#btn_login_text:hover {
  background-color: rgba(0, 0, 0, 0.15);
}
#btn_skin {
  background-color: transparent;
  border-image: url('''+ assetsUrl('icon', 'skin.png') +''');
}
#btn_skin:hover {
  background-color: rgba(0, 0, 0, 0.1);
}
#btn_setting {
  background-color: transparent;
  border-image: url('''+ assetsUrl('icon', 'setting.png') +''');
}
#btn_setting:hover {
  background-color: rgba(0, 0, 0, 0.1);
}
#btn_message {
  background-color: transparent;
  border-image: url('''+ assetsUrl('icon', 'message.png') +''');
}
#btn_message:hover {
  background-color: rgba(0, 0, 0, 0.1);
}
.btn_big {
  border-image: url('''+ assetsUrl('icon', 'big.png') +''');
}
.btn_restore {
  border-image: url('''+ assetsUrl('icon', 'restore.png') +''');
}
#btn_small {
  border-image: url('''+ assetsUrl('icon', 'small.png') +''');
}
#btn_close {
  border-image: url('''+ assetsUrl('icon', 'close.png') +''');
}
#btn_close:hover {
  background-color: rgba(255, 0, 0, 0.7);
}
#btn_change, #btn_small, #btn_close {
  border-radius: 6px;
  background-color: rgba(255, 255, 255, 0.2);
}

/* 左侧栏样式 */
#leftbar_container .QPushButton {
  color: #333;
  font-size: 16px;
}
'''


# 程序主窗口的类
class MainWindow(QMainWindow):
  def __init__(self, param:Param):
    super().__init__()
    self.param = param
    self.callback = Callback()
    # 设置全局样式
    self.setStyleSheet(assetsRead('UI', 'style.qss'))
    # 设置阴影效果
    setShadowEffect(self)
    self.setWindowTitle(getSetting("APP_TITLE"))
    self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 去除原来的边框
    self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 透明背景
    # 添加窗口移动功能
    self.win = MoveWin(self, param, "main_window_position")
    # 创建UI挂载节点
    self.ui = QWidget()
    self.ui.setStyleSheet(main_window_style())
    self.setCentralWidget(self.ui)
    # 渲染UI
    self.widgetsController:WidgetsController = WidgetsController(render(self.ui, template, {
      "title": getSetting('APP_TITLE'),
    })['widgets'])
    # 绑定按钮事件
    self.register('btn_close', 'clicked', self.closePage)
    self.register('btn_small', 'clicked', self.showMinimized)
    self.register('btn_change', 'clicked', self.toggleMaximize)
    # 设置初始状态
    self.setClass('btn_change', 'btn_restore' if self.param.get("is_maximized", False) else 'btn_big')


  def register(self, id:str, signal:str, callback):
    self.widgetsController.register(id, signal, callback)


  def setClass(self, id:str, className:str):
    self.widgetsController.setClass(id, className)


  def getWidget(self, id:str) -> QWidget|QLayout:
    return self.widgetsController.getWidget(id)


  def closePage(self):
    """关闭窗口并保存位置参数"""
    self.close()
    self.callback.run('close')


  def toggleMaximize(self):
    """切换窗口最大化/还原状态"""
    if not self.param.get("is_maximized", False):
      # 1. 记录当前窗口状态（原始位置和尺寸）
      original_position = self.getPosition()
      self.param.set('original_position', original_position)
      print("记录窗口位置和尺寸:", original_position)
      # 2. 切换到最大化状态
      self.showMaximized()
      current_position = self.getPosition()
      self.updateMainUI(current_position)
      print("切换到最大化状态，当前窗口位置和尺寸:", current_position)
      self.win.setPosition(20)  # 增加20像素以适应最大化边框
      self.param.set("is_maximized", True)
      self.widgetsController.setClass('btn_change', 'btn_restore')
    else:
      # 1. 还原到原始位置和尺寸
      position = self.param.get('original_position')
      print("还原窗口位置和尺寸:", position)
      self.setGeometry(*position)
      self.updateMainUI(position)
      self.win.setPosition()
      self.param.set("is_maximized", False)
      self.widgetsController.setClass('btn_change', 'btn_big')


  def getPosition(self):
    """获取窗口位置和尺寸"""
    rect = self.geometry()
    return [rect.left(), rect.top(), rect.width(), rect.height()]
  

  def updateMainUI(self, position):
    """更新主界面位置和尺寸"""
    self.widgetsController.getWidget('main-ui').setFixedHeight(position[3])
    self.widgetsController.getWidget('main-ui').setFixedWidth(position[2])

  
  def setUserInfo(self, userName:str, avatarPath:str):
    if not os.path.exists(avatarPath):
      avatarPath = assetsUrl('image', 'avatar.png')
    self.widgetsController.getWidget('btn_login_icon').setStyleSheet(f'border-image:url({avatarPath});')
    self.widgetsController.getWidget('btn_login_text').setText(userName[:3])


  def setAppStyle(self):
    default_theme = Config().default_theme
    setting = Param(self.param.pathJoin("userPath", "setting.json"), default_theme)
    skin_id = setting.get("skinId", default_theme["skinId"])
    
    # 获取当前皮肤样式
    skin_styles = setting.get("skinStyle", default_theme['skinStyle'])
    style = next((s for s in skin_styles if s['id'] == skin_id), None)
    if not style:
        raise ValueError(f"Skin style with id '{skin_id}' not found")
    
    # 处理背景图片路径
    image_path = style['app_bg_image'].replace('\\', '/') if isinstance(style['app_bg_image'], str) else ''
    if not os.path.exists(image_path):
        image_path = assetsUrl('skin', 'app_bg_image_1.png')
    
    # 设置头部和主体样式
    app_header_style = s2t({"background-color": style['header_bg_color']})
    app_main_style = s2t({
      "background-color": style['main_bg_color'],
      "border-image": f"url('{image_path}') stretch",
    })
    self.getWidget('app_header').setStyleSheet(f'#app_header{'{'}{app_header_style}{'}'}')
    self.getWidget('app_main').setStyleSheet(f'#app_main{'{'}{app_main_style}{'}'}')