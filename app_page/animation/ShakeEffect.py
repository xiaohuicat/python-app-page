from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QPropertyAnimation, QPoint


class ShakeEffect:
  def __init__(self, target:QWidget) -> None:
    if hasattr(target, "_shake_animation"):
      # 如果已经有对象则跳过
      return
    
    animation = QPropertyAnimation(target, b'pos', target)
    target._shake_animation = animation
    animation.finished.connect(lambda: delattr(target, '_shake_animation'))

    pos = target.pos()
    x, y = pos.x(), pos.y()

    animation.setDuration(100)
    animation.setLoopCount(2)
    animation.setKeyValueAt(0, QPoint(x, y))
    animation.setKeyValueAt(0.09, QPoint(x + 2, y - 2))
    animation.setKeyValueAt(0.18, QPoint(x + 4, y - 4))
    animation.setKeyValueAt(0.27, QPoint(x + 2, y - 6))
    animation.setKeyValueAt(0.36, QPoint(x + 0, y - 8))
    animation.setKeyValueAt(0.45, QPoint(x - 2, y - 10))
    animation.setKeyValueAt(0.54, QPoint(x - 4, y - 8))
    animation.setKeyValueAt(0.63, QPoint(x - 6, y - 6))
    animation.setKeyValueAt(0.72, QPoint(x - 8, y - 4))
    animation.setKeyValueAt(0.81, QPoint(x - 6, y - 2))
    animation.setKeyValueAt(0.90, QPoint(x - 4, y - 0))
    animation.setKeyValueAt(0.99, QPoint(x - 2, y + 2))
    animation.setEndValue(QPoint(x, y))

    animation.start()