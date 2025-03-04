from PySide6.QtWidgets import QMainWindow, QGraphicsDropShadowEffect
from PySide6.QtGui import QGuiApplication
from PySide6 import QtCore, QtGui
from app_page_core import Param, Callback
from ..animation import MoveWin
from ..config import small_page_icon, maximize_page_icon, APP_TITLE
from ..core import Setting
from ..core.ui_main import Ui_MainWindow
from ..utils import setupUiFromSetting


# 程序主窗口的类
class MainWindow(QMainWindow):
    def __init__(self, system_param:Param):
        super().__init__()
        self.system_param = system_param
        self.callback = Callback()
        self.ui = setupUiFromSetting(self, "Ui_MainWindow")
        self.normal_window_rect = [570, 79, 1080, 746]
        self.current_window_rect = [*self.normal_window_rect]

        self.setWindowTitle(Setting.getSetting("APP_TITLE", APP_TITLE))
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 去除原来的边框
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 透明背景
        self.ui.btn_change.clicked.connect(self.restore_or_maximize_window)
        self.ui.btn_mini.clicked.connect(self.showMinimized)
        self.ui.label_logo.setText(Setting.getSetting("APP_TITLE", APP_TITLE))
        self.isMaximized = False

        self.effect_shadow = QGraphicsDropShadowEffect(self)
        self.effect_shadow.setOffset(0,0) # 偏移
        self.effect_shadow.setBlurRadius(16) # 阴影半径
        self.effect_shadow.setColor(QtCore.Qt.gray) # 阴影颜色
        self.ui.centralwidget.setGraphicsEffect(self.effect_shadow) # 将设置套用到widget窗口中

        self.move_win = MoveWin(self, system_param, "main_window_position")
        self.isMaximized = self.move_win.window_position[2] != 1080
        if self.isMaximized:
            self.ui.btn_change.setIcon(QtGui.QIcon(Setting.getSetting("small_page_icon", small_page_icon)))
        else:
            self.ui.btn_change.setIcon(QtGui.QIcon(Setting.getSetting("maximize_page_icon", maximize_page_icon)))
        self.current_window_rect = [*self.move_win.window_position]

    def restore_or_maximize_window(self):  # 放大缩小
        if self.isMaximized:
            self.isMaximized = False
            if self.current_window_rect[2] != 1080:
                self.current_window_rect = [*self.normal_window_rect]
            self.setGeometry(*self.current_window_rect)
            self.ui.btn_change.setIcon(QtGui.QIcon(Setting.getSetting("maximize_page_icon", maximize_page_icon)))
            self.callback.run("restore_window", self.current_window_rect)
        else:
            self.isMaximized = True
            raw = self.geometry()
            self.current_window_rect = [raw.x(),raw.y(),raw.width(),raw.height()]
            rect = QGuiApplication.primaryScreen().availableGeometry()
            self.setGeometry(-10,-10,rect.width()+20,rect.height()+45)
            self.ui.btn_change.setIcon(QtGui.QIcon(Setting.getSetting("small_page_icon", small_page_icon)))
            self.callback.run("restore_window", [0,0,rect.width(),rect.height()])
        self.move_win.saveCurrentPosition()