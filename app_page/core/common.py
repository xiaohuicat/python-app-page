from PySide6.QtWidgets import QWidget


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