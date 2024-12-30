from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QFont, QFontMetrics
from PySide6.QtGui import QGuiApplication
from ..animation.FadeEffect import FadeEffect
from ..utils.loadUI import loadUI
from app_page import Callback

color_dict = {
    'success': '#28be28',
    'fail': '#e64035',
    'warning': '#eaa640',
    'default': '#4d4d4d'
}

class Tips(QWidget):
    def __init__(self, message, type='default', pos=None):
        super().__init__()
        self.callback = Callback()

        self.ui = loadUI('./assets/UI/tips.ui')

        self.setWindowTitle("提示消息")
        self.ui.tips.setText(message)
        self.ui.tips.setStyleSheet(f'background-color: {color_dict[type]};')
        width, height = self.calculate_text_rect(message, 300, 1)
        self.width = width
        self.height = height

        self.ui.tips.setFixedWidth(width + 20)
        self.ui.tips.setFixedHeight(height + 20)
        self.setFixedWidth(width + 60)
        self.setFixedHeight(height + 60)

        self.setPos(pos)

        # 创建垂直布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)

        # 设置弹出窗口的位置
        # self.setGeometry(pos[0], pos[1], 200, 100)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)  # 设置窗口置顶

        self.setWindowFlag(Qt.FramelessWindowHint)  # 去除原来的边框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景

        # 添加淡入淡出的动画
        self.fadeEffect = FadeEffect(self, 200, self.close)
        self.fadeEffect.show()     

    def setPos(self, pos):
        if not pos:
            rect = QGuiApplication.primaryScreen().availableGeometry()
            pos = [rect.width()/2, rect.height()/2]
        self.setGeometry(int(pos[0]-(self.width+60)/2), int(pos[1]-(self.height+60)/2), self.width+60, self.height+60)

    def showEvent(self, event):
        # 在窗口显示时关闭定时器
        self.startTimer(2000)  # 设置定时器，2秒后关闭窗口

    def timerEvent(self, event):
        # 定时器触发时关闭窗口
        self.killTimer(event.timerId())
        self.fadeEffect.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.callback.run("close")
        return super().closeEvent(event)
    
    # 计算矩形宽高
    def calculate_text_rect(self, text, max_width, line_spacing_factor):
        # 设置字体，确保与实际显示的字体相匹配
        font = QFont()
        font.setPointSize(12)  # 设置字号
        self.setFont(font)

        # 使用QFontMetrics测量文本的边界矩形
        metrics = QFontMetrics(font)

        # 分割文本，计算每一行的宽度和高度
        lines = text.split('\n')
        line_widths = [metrics.boundingRect(line).width() for line in lines]
        max_line_width = max(line_widths)
        total_height = sum(metrics.boundingRect(line).height() for line in lines)

        # 如果宽度小于等于最大宽度，直接返回实际宽度和高度
        if max_line_width <= max_width:
            return max_line_width, total_height

        # 如果宽度大于最大宽度，计算需要的行数，并返回新的宽度和高度
        num_lines = (max_line_width + max_width - 1) // max_width
        new_width = max_width
        new_height = num_lines * total_height * line_spacing_factor

        return new_width, new_height