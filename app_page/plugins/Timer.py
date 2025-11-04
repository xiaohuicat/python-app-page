import time
import random
import string
from app_page import Page
from app_page.utils import timestamp


def random_string(length: int) -> str:
    """生成指定长度的随机字母字符串"""
    return ''.join(random.choices(string.ascii_letters, k=length))


class Timer(Page):
    def __init__(self, callback, delay: int = 0, immediately: bool = True):
        super().__init__()
        # 生成唯一计时器ID
        self._timer_thread_id = f"timer_{timestamp()}_{random_string(6)}"
        self._callback = callback
        self._delay = delay  # 确保延迟为非负值
        self._is_running = False  # 新增运行状态标记

        if immediately:
            self.start()

    def start(self) -> None:
        """启动计时器（若未运行）"""
        if self._is_running:
            return

        self._is_running = True
        self.threadManager.add({
            'id': self._timer_thread_id,
            'function': self._delay_execution,  # 分离延迟逻辑
            'callback': self._on_callback,
        }, True)

    def _delay_execution(self) -> None:
        """执行延迟等待（可扩展添加中断逻辑）"""
        if self._delay > 0:
            time.sleep(self._delay)

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
            self.threadManager.run(self._timer_thread_id)

    def set_callback(self, callback) -> None:
        """更新回调函数"""
        self._callback = callback

    def set_delay(self, delay: int) -> None:
        """新增：更新延迟时间"""
        if delay >= 0:
            self._delay = delay

    def stop(self) -> None:
        """停止计时器（更直观的命名）"""
        if self._is_running:
            self._is_running = False
            self.threadManager.remove(self._timer_thread_id)

    # 保留clear方法作为兼容接口
    def clear(self) -> None:
        self.stop()