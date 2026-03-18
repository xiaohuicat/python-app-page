from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel
from app_page_core import Store
from ..animation import FadeEffect

color_dict = {
    'success': '#28be28',
    'fail': '#e64035',
    'warning': '#eaa640',
    'default': "#118cff"
}

class Tips(QWidget):
    """拟态提示框组件"""
    def __init__(self, message="拟态提示消息", type='default'):
        super().__init__()
        # 去除窗口边框，背景透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20) # 设置外边距
        
        # 创建内容标签
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True) # 允许自动换行
        # 设置窗口置顶
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 关键：设置拟态样式表
        self.setStyleSheet("""
            border-radius: 8px; /* 大圆角 */
            border: none;
        """)
        
        # 设置标签样式
        self.label.setStyleSheet(f"""
            background-color: {color_dict.get(type, '#4d4d4d')};
            font-size: 14px;
            padding: 8px;
            color: #ffffff;
        """)

        main_layout.addWidget(self.label)
        self.adjustSize()
        self.center()
        # 添加淡入淡出的动画
        self.fadeEffect = FadeEffect(self, 200)
        self.fadeEffect.show()

    def center(self):
        """居中显示在屏幕或父窗口"""
        # 获取屏幕尺寸居中
        screen_geometry = Store().get('mainWin').geometry()
        # 帮我实现消息框在父窗口内居中显示
        x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - self.height()) // 2
        # 设置消息
        self.setGeometry(x, y, self.width(), self.height())

    def showEvent(self, event):
        # 在窗口显示时关闭定时器
        self.startTimer(2000)  # 设置定时器，2秒后关闭窗口

    def timerEvent(self, event):
        # 定时器触发时关闭窗口
        self.killTimer(event.timerId())
        self.fadeEffect.close()