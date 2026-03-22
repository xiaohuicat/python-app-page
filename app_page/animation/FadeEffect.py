from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QPropertyAnimation


class FadeEffect:
    """
    为Qt Widget窗口提供淡入淡出的过渡效果
    
    该类通过QPropertyAnimation控制窗口的windowOpacity属性，
    实现窗口的平滑显示/关闭动画，避免直接显示/关闭的生硬效果。
    每个窗口实例只会创建一个动画对象，防止重复创建导致的动画冲突。
    """
    
    def __init__(self, target: QWidget, duration: int = 200, finish=None) -> None:
        """
        初始化淡入淡出效果
        
        Args:
            target (QWidget): 要应用动画效果的目标窗口控件
            duration (int, optional): 动画持续时间（毫秒），默认200ms
            finish (callable, optional): 淡出动画结束后执行的回调函数，
                若未传入或非可调用对象，默认执行target.close()
        
        Notes:
            若目标窗口已存在_fade_animation属性（已有动画对象），则直接返回，
            避免重复创建动画实例导致的冲突
        """
        # 检查目标窗口是否已有动画对象，有则直接返回
        if hasattr(target, "_fade_animation"):
            return
        
        # 创建窗口透明度属性动画
        target._fade_animation = QPropertyAnimation(target, b'windowOpacity')
        target._fade_animation.setDuration(duration)  # 设置动画持续时间

        self._target = target
        # 确定动画结束后的回调函数，默认关闭窗口
        self._finish = finish if callable(finish) else target.close
        self.is_exec = False

    def show(self, is_exec=False):
        """
        执行窗口淡入显示动画
        
        先停止当前可能正在运行的动画，设置透明度从0到1的动画过程，
        启动动画并显示窗口，实现从完全透明到不透明的淡入效果。
        """
        self.is_exec = is_exec
        # 停止当前动画（防止动画叠加）
        self._target._fade_animation.stop()
        # 设置动画起始透明度（完全透明）
        self._target._fade_animation.setStartValue(0)
        # 设置动画结束透明度（完全不透明）
        self._target._fade_animation.setEndValue(1)
        # 启动淡入动画
        self._target._fade_animation.start()
        # 显示窗口（确保窗口可见）
        if is_exec:
            if hasattr(self._target, "exec"):
                self._target.exec()
        else:
            self._target.show()

    def close(self):
        """
        执行窗口淡出关闭动画
        
        先停止当前可能正在运行的动画，设置透明度从1到0的动画过程，
        绑定动画结束回调函数，启动动画，实现从不透明到完全透明的淡出效果。
        """
        # 停止当前动画（防止动画叠加）
        self._target._fade_animation.stop()
        # 绑定动画结束后的回调函数
        self._target._fade_animation.finished.connect(self._on_finish)
        # 设置动画起始透明度（完全不透明）
        self._target._fade_animation.setStartValue(1)
        # 设置动画结束透明度（完全透明）
        self._target._fade_animation.setEndValue(0)
        # 启动淡出动画
        self._target._fade_animation.start()

    def _on_finish(self):
        """
        淡出动画结束后的回调处理函数（内部方法）
        
        移除目标窗口的动画属性，执行预设的结束回调（默认关闭窗口），
        并清空实例属性，释放资源。
        """
        delattr(self._target, '_fade_animation')
        if not self.is_exec:
            self._finish()
        else:
            if hasattr(self._target, 'accept'):
                self._target.accept()
            else:
                self._finish()
        self._target = None
        self._finish = None