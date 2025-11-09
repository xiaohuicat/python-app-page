from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget


def setShadowEffect(target:QWidget, options:dict={}):
    """设置阴影效果"""
    shadow = QGraphicsDropShadowEffect(target)
    shadow.setOffset(*options.get('offset', [0,0])) # 偏移
    shadow.setBlurRadius(options.get('radius', 16)) # 阴影半径
    shadow.setColor(options.get('color', '#000')) # 阴影颜色
    target.setGraphicsEffect(shadow) # 将设置套用到widget窗口中


def updateStyle(target:QWidget):
    """更新组件样式"""
    target.style().unpolish(target)
    target.style().polish(target)