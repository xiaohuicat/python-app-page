from PySide6.QtWidgets import QWidget, QScrollArea
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from typing import Literal


def smoothScroll(
  scroll_area: QScrollArea,
  scroll_axis: Literal["vertical", "horizontal"] = "vertical",  # 滚动轴：vertical/horizontal
  target: int = -1,  # 目标位置：-1=滚动到最末端；其他值=指定位置
  duration: int = 200,  # 动画时长(ms)
  easing_curve: QEasingCurve = QEasingCurve.OutQuad  # 动画缓动曲线
):
  """
  平滑滚动QScrollArea到指定位置
  """
  # 参数校验
  if scroll_axis not in ["vertical", "horizontal"]:
    raise ValueError(f"无效的滚动轴: {scroll_axis}，仅支持 'vertical' 或 'horizontal'")
  
  if not isinstance(scroll_area, QScrollArea):
    raise TypeError(f"scroll_area必须是QScrollArea实例，当前类型: {type(scroll_area)}")
  
  # 获取对应滚动条
  if scroll_axis == "vertical":
    scroll_bar = scroll_area.verticalScrollBar()
  else:
    scroll_bar = scroll_area.horizontalScrollBar()
  
  if scroll_bar is None:
    raise RuntimeError(f"滚动区域无{scroll_axis}滚动条")
  
  # 计算当前值和目标值
  currentValue = scroll_bar.value()
  targetValue = scroll_bar.maximum() if target == -1 else target

  print(f"{scroll_axis}滚动: 当前值={currentValue}, 目标值={targetValue}")
  
  # 已在目标位置则无需动画
  if currentValue == targetValue:
    return
  
  # 创建平滑滚动动画
  animation = QPropertyAnimation(scroll_bar, b"value")
  animation.setDuration(duration)
  animation.setStartValue(currentValue)
  animation.setEndValue(targetValue)
  animation.setEasingCurve(easing_curve)
  
  # 启动动画（结束后自动删除）
  animation.start(QPropertyAnimation.DeleteWhenStopped)
  
  # 绑定动画对象防止被垃圾回收
  scroll_area.__scroll_animation = animation