from PySide6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QWidget, QScrollArea


def scrollToBottom(parent:QWidget|None, scroll_area:QScrollArea|str):
  def scroll():
    # 如果是字符串，寻找滚动区域
    if isinstance(scroll_area, str):
      _scroll_area = parent.findChild(QWidget, scroll_area)
    else:
      _scroll_area = scroll_area
    
    height = _scroll_area.verticalScrollBar().maximum()
    _scroll_area.verticalScrollBar().setValue(height)

  # 创建一个定时器
  QTimer.singleShot(100, scroll)


def smoothScrollToBottom(parent:QWidget|None, scroll_area:QScrollArea|str):
    # 如果是字符串，寻找滚动区域
    if isinstance(scroll_area, str):
      scrollArea = parent.findChild(QWidget, scroll_area)
    else:
      scrollArea = scroll_area  
  
    # 获取滚动条的最大值  
    maxValue = scrollArea.verticalScrollBar().maximum()  
    # 获取当前滚动条的值  
    currentValue = scrollArea.verticalScrollBar().value()
    
    print(maxValue, currentValue)

    # 创建动画
    animation = QPropertyAnimation(scrollArea.verticalScrollBar(), b"value")  
    animation.setDuration(200)  # 设置动画持续时间为500毫秒  
    animation.setStartValue(currentValue)  
    animation.setEndValue(maxValue)  
    animation.setEasingCurve(QEasingCurve.OutQuad)  # 设置缓动曲线  
    animation.start(QPropertyAnimation.DeleteWhenStopped)  # 开始动画，并在结束时删除动画对象
    
    scrollArea.__scroll_to_bottom_animation = animation