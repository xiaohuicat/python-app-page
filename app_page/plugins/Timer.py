import time
from app_page import Page
from app_page.utils import timestamp
from nanoid import generate
from typing import Callable

class Timer(Page):
    def __init__(self, callback: Callable, interval: int = 0, immediately: bool = True):
        """
        定时器类
            :param callback: 回调函数
            :param interval: 定时器间隔
            :param immediately: 是否立即启动
        """
        super().__init__()
        # 生成唯一计时器ID
        self._timer_thread_id = f"timer_{timestamp()}_{generate(size=6)}"
        self._callback = callback
        self._interval = interval
        self._is_running = False

        if immediately:
            self.start()

    def start(self) -> None:
        """启动计时器（若未运行）"""
        if self._is_running:
            return

        self._is_running = True
        self.threadManager.add(
            thread_id=self._timer_thread_id,
            function=self._interval_execution,
            callback=self._on_callback,
            start=True,
            once=False
        )

    def _interval_execution(self) -> None:
        """执行延迟等待（可扩展添加中断逻辑）"""
        if self._interval > 0:
            time.sleep(self._interval)

    def _on_callback(self, *args) -> None:
        """计时器回调处理"""
        if not self._is_running:  # 检查是否已停止
            return

        # 执行用户回调
        if callable(self._callback):
            try:
                self._callback()
            except Exception as e:
                # 捕获回调异常，避免计时器崩溃
                print(f"Timer callback error: {e}")

        # 继续下一轮计时
        if self._is_running:
            self.threadManager.start(self._timer_thread_id)

    def set_callback(self, callback: Callable) -> None:
        """更新回调函数"""
        self._callback = callback

    def set_interval(self, interval: int) -> None:
        """新增：更新延迟时间"""
        if interval >= 0:
            self._interval = interval

    def stop(self) -> None:
        """停止计时器（更直观的命名）"""
        if self._is_running:
            self._is_running = False
            self.threadManager.remove(self._timer_thread_id)

    def clear(self) -> None:
        self.stop()