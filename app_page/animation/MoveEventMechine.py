from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent


class MoveEventMechine:
    """
    鼠标移动事件处理器
    用于监听目标控件的鼠标移动事件，并根据指定的鼠标按键类型触发回调
    """
    def __init__(self, target, callback, type="both"):
        """
        初始化事件处理器
        
        Args:
            target: 目标控件对象
            callback: 事件触发时的回调函数
            type: 监听的鼠标按键类型，可选值：left/right/both，默认both
        """
        self.target = target
        self.callback = callback
        self.isClick = None  # 标记鼠标是否处于按下状态
        self.type = type
  
    def start(self, event: QMouseEvent):
        """
        开始监听（鼠标按下时调用）
        
        Args:
            event: 鼠标事件对象
        """
        self.isClick = True
  
    def clear(self, event: QMouseEvent):
        """
        清除监听状态（鼠标移动时调用）
        
        Args:
            event: 鼠标事件对象
        """
        self.isClick = False
        QPushButton.mouseMoveEvent(self.target, event)
  
    def stop(self, event: QMouseEvent):
        """
        停止监听并触发回调（鼠标释放时调用）
        
        Args:
            event: 鼠标事件对象
        
        Raises:
            Exception: 当type参数值不合法时抛出异常
        """
        if self.isClick:
            if self.type == "left" and event.button() == Qt.LeftButton:
                self.callback(event)
            elif self.type == "right" and event.button() == Qt.RightButton:
                self.callback(event)
            elif self.type == "both":
                self.callback(event)
            elif self.type != "left" and self.type != "right" and self.type != "both":
                raise Exception("button must be left or right or both")