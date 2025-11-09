from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QPropertyAnimation


class FadeEffect:
  def __init__(self, target:QWidget, duration=200, finish=lambda: print("FadeEffect>finish")) -> None:
    if hasattr(target, "_fade_animation"):
      # 如果已经有对象则跳过
      return
    
    target._fade_animation = QPropertyAnimation(target, b'windowOpacity')
    target._fade_animation.setDuration(duration)  # 持续事件1秒

    self.target = target
    self.finish = finish

  def show(self):
    self.target._fade_animation.stop()
    self.target._fade_animation.setStartValue(0)
    self.target._fade_animation.setEndValue(1)
    self.target._fade_animation.start()


  def close(self):
    self.target._fade_animation.stop()
    self.target._fade_animation.finished.connect(self.finish)
    self.target._fade_animation.setStartValue(1)
    self.target._fade_animation.setEndValue(0)
    self.target._fade_animation.start()
