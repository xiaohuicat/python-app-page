from PySide6.QtWidgets import QWidget
from typing import Callable

def setShadowEffect(target:QWidget, options:dict={}):
    """设置阴影效果"""
    from PySide6.QtWidgets import QGraphicsDropShadowEffect
    shadow = QGraphicsDropShadowEffect(target)
    shadow.setOffset(*options.get('offset', [0,0])) # 偏移
    shadow.setBlurRadius(options.get('radius', 20)) # 阴影半径
    shadow.setColor(options.get('color', '#888')) # 阴影颜色
    target.setGraphicsEffect(shadow) # 将设置套用到widget窗口中


def setBlurEffect(target:QWidget, radius:int=10):
    """设置模糊效果"""
    from PySide6.QtWidgets import QGraphicsBlurEffect
    blur = QGraphicsBlurEffect(target)
    blur.setBlurRadius(radius)
    blur.setBlurHints(QGraphicsBlurEffect.QualityHint)
    target.setGraphicsEffect(blur)


def updateStyle(target:QWidget):
    """更新组件样式"""
    target.style().unpolish(target)
    target.style().polish(target)


def tryRun(func:Callable, *args, **kwargs):
    """尝试执行函数，捕获异常并打印"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"tryRun执行函数 {func.__name__} 出错：", e)


def set_relative_bottom(target:QWidget, parent:QWidget, margin:int=30):
    """水平居中，贴近底部"""
    x = (parent.width() - target.width()) // 2
    y = parent.height() - target.height() - margin
    target.move(x, y)


def set_relative_top(target:QWidget, parent:QWidget, margin:int=30):
    """水平居中，贴近顶部"""
    x = (parent.width() - target.width()) // 2
    y = margin
    target.move(x, y)


def set_relative_center(target:QWidget, parent:QWidget):
    """水平居中，垂直居中"""
    x = (parent.width() - target.width()) // 2
    y = (parent.height() - target.height()) // 2
    target.move(x, y)


def set_relative_left(target:QWidget, parent:QWidget, margin:int=30):
    """水平靠左，垂直居中"""
    x = margin
    y = (parent.height() - target.height()) // 2
    target.move(x, y)


def set_relative_right(target:QWidget, parent:QWidget, margin:int=30):
    """水平靠右，垂直居中"""
    x = parent.width() - target.width() - margin
    y = (parent.height() - target.height()) // 2
    target.move(x, y)