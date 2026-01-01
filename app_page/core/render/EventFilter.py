from PySide6.QtCore import QObject


class EventFilter(QObject):
    """自定义事件过滤器，处理卡片点击"""
    def __init__(self, callback):
        super().__init__()
        self.callback = callback


    def eventFilter(self, watched, event):
        ret = self.callback(watched, event)
        if ret:
            return True
        return super().eventFilter(watched, event)