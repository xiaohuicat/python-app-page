from PySide6.QtCore import QThread, Signal
from typing import Union, Callable

class EasyThread(QThread):
    """
    简易线程包装类，支持将普通函数放入 QThread 中运行并返回结果。
    """
    response = Signal(object)  # 任务完成后的结果信号

    def __init__(self, function: Callable, payload=None, callback: Callable = None):
        """
        初始化函数
            :param function: 需要在线程中执行的函数
            :param payload: 函数参数，支持 dict (kwargs), list/tuple (args), 或单个变量
            :param callback: 结果回调函数 (接收 response 信号)
        """
        super().__init__()
        self.function = function
        self.payload = payload

        if callback and callable(callback):
            self.response.connect(callback)

    def run(self):
        try:
            # 兼容有参和无参调用
            if self.payload is not None:
                ret = self.function(self.payload)
            else:
                ret = self.function()
            self.response.emit(ret)
        except Exception as e:
            print(f"Thread execution error: {e}")


class ThreadManager:
    """
    QThread 线程管理器，负责线程的创建、生命周期管理、批量操作及动态筛选控制。
    """
    def __init__(self):
        self._tasks = {}  # 存储格式 {thread_id: EasyThread_Object}

    def add(self, thread_id: str, function: Callable, payload=None, callback: Callable = None, start=False, once=True):
        """
        便捷添加并配置任务。
            :param thread_id: 任务唯一标识
            :param function: 执行函数
            :param payload: 函数参数
            :param callback: 结果回调函数 (接收 response 信号)
            :param start: 是否立即启动
            :param once: 是否运行结束自动清除，默认 True
        """
        thread = EasyThread(function, payload, callback)
        self.add_thread(thread_id, thread, start, once)

    def add_thread(self, thread_id: str, thread: EasyThread, start=False, once=True):
        """
        将现有的 EasyThread 实例加入管理器。
            :param thread_id: 任务唯一标识
            :param thread: 用户自定义，继承自 EasyThread 的线程实例
            :param start: 是否立即启动，默认 False
            :param once: 是否运行结束自动清除，默认 True
        """
        # 如果已存在同名任务且在运行，先停止并移除
        if thread_id in self._tasks:
            self.stop(thread_id, wait=True)
        
        # 记录任务
        self._tasks[thread_id] = thread

        if once:
            # 线程结束后自动从管理字典中移除
            thread.finished.connect(lambda: self._tasks.pop(thread_id, None))
        
        if start:
            thread.start()

    def get_thread(self, thread_id: Union[str, Callable]) -> Union[EasyThread, None]:
        """
        获取线程对象。
            :param thread_id: 任务 ID (str) 或 筛选函数 (Callable)
            :return: EasyThread 实例或 None
        """
        if callable(thread_id):
            for tid, thread in self._tasks.items():
                if thread_id(tid):
                    return thread
            return None
        return self._tasks.get(thread_id)

    def start(self, thread_id: Union[str, Callable], payload=None):
        """
        启动已存在的任务，支持通过筛选函数启动第一个符合条件的闲置线程。
            :param thread_id: 任务唯一标识 (str) 或 筛选函数 (如 lambda tid: tid.startswith("io_"))
            :param payload: 函数参数，若提供则更新原参数
        """
        # 如果是函数，优先寻找匹配且非运行状态的线程
        target_thread: EasyThread = None
        if callable(thread_id):
            for tid, thread in self._tasks.items():
                if thread_id(tid) and not thread.isRunning():
                    target_thread = thread
                    break
        else:
            target_thread = self._tasks.get(thread_id)

        if target_thread:
            if payload is not None:
                target_thread.payload = payload
            if not target_thread.isRunning():
                target_thread.start()
        else:
            print(f"Start failed: No available task found for '{thread_id}'.")

    def has(self, thread_id: Union[str, Callable]) -> bool:
        """
        检查指定任务是否存在于管理器中。
            :param thread_id: 任务唯一标识 (str) 或 筛选函数 (Callable)
        """
        if callable(thread_id):
            return any(thread_id(tid) for tid in self._tasks.keys())
        return thread_id in self._tasks

    def has_free(self, thread_id: Union[str, Callable]) -> bool:
        """
        判断指定 ID 或符合规则的任务是否存在且处于闲置状态。
            :param thread_id: 任务唯一标识 (str) 或 筛选函数 (Callable)
        """
        if callable(thread_id):
            return any(thread_id(tid) and not thread.isRunning() for tid, thread in self._tasks.items())
        
        thread: EasyThread = self._tasks.get(thread_id)
        return thread is not None and not thread.isRunning()

    def count(self, filter_rule: Union[Callable, None] = None, thread_type: str = "all") -> int:
        """
        统计线程数量。
            :param filter_rule: ID 筛选函数，如 `lambda tid: tid.startswith("io_")`
            :param thread_type: 统计类型 'all' (全部), 'free' (空闲), 'used' (运行中)
        """
        count = 0
        for tid, thread in list(self._tasks.items()):
            if filter_rule and not filter_rule(tid):
                continue
            
            is_running = thread.isRunning()
            if thread_type == "all":
                count += 1
            elif thread_type == "free" and not is_running:
                count += 1
            elif thread_type == "used" and is_running:
                count += 1
        return count

    def stop(self, thread_id: Union[str, Callable], wait=False):
        """
        停止并销毁特定线程（支持通过规则匹配第一个符合条件的线程）。
            :param thread_id: 任务唯一标识 (str) 或 筛选函数 (Callable)
            :param wait: 是否阻塞等待线程安全退出
        """
        target_tid = None
        if callable(thread_id):
            for tid in list(self._tasks.keys()):
                if thread_id(tid):
                    target_tid = tid
                    break
        else:
            target_tid = thread_id

        thread: EasyThread = self._tasks.get(target_tid)
        if thread:
            if thread.isRunning():
                thread.quit()
                if wait:
                    thread.wait()
                else:
                    thread.terminate() 
            
            self._tasks.pop(target_tid, None)
            thread.deleteLater()

    def stop_all(self, wait=False):
        """
        停止管理器中的所有线程。
            :param wait: 是否阻塞等待线程安全退出
        """
        for tid in list(self._tasks.keys()):
            self.stop(tid, wait)

    def remove(self, thread_id: Union[str, Callable, None] = None, wait=False):
        """
        根据规则批量移除任务，移除时自动停止任务。
            :param thread_id: None (全删), str (删特定), callable (按规则筛选删除所有匹配项)
            :param wait: 是否阻塞等待线程安全退出
        """
        if thread_id is None:
            self.stop_all(wait)
            return

        if callable(thread_id):
            targets = [tid for tid in list(self._tasks.keys()) if thread_id(tid)]
            for tid in targets:
                self.stop(tid, wait)
            return

        if thread_id in self._tasks:
            self.stop(thread_id, wait)