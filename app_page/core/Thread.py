from PySide6.QtCore import QThread, Signal


class EasyThread(QThread):
    response = Signal(object)

    def __init__(self, function, payload=None):
        super().__init__()
        self.function = function
        self.payload = payload
        # 任务完成后自动销毁对象，防止内存泄漏
        self.finished.connect(self.deleteLater)

    def run(self):
        try:
            # 兼容有参和无参调用
            if self.payload is not None:
                if isinstance(self.payload, dict):
                    ret = self.function(**self.payload)
                elif isinstance(self.payload, (list, tuple)):
                    ret = self.function(*self.payload)
                else:
                    ret = self.function(self.payload)
            else:
                ret = self.function()
            self.response.emit(ret)
        except Exception as e:
            print(f"Thread execution error: {e}")


class ThreadManager:
    def __init__(self):
        self._tasks = {}  # 使用字典代替列表，查询复杂度 O(1)

    def add(self, thread_id, function, payload=None, callback=None, start=False):
        """
        Args:
            thread_id: 唯一标识
            function: 执行函数
            payload: 参数
            callback: 回调函数
            start: 是否立即启动
        """
        thread = EasyThread(function, payload)
        self.add_thread(thread_id, thread, callback, start)

    def add_thread(self, thread_id:str, thread:EasyThread, callback=None, start=False):
        # 如果已存在同名任务且在运行，先停止（或根据业务逻辑跳过）
        if thread_id in self._tasks:
            self.stop(thread_id)
            self.remove(thread_id)
        
        if callback:
            thread.response.connect(callback)

        # 记录任务
        self._tasks[thread_id] = thread
        
        # 线程结束后自动从管理字典中移除，避免野指针
        thread.finished.connect(lambda: self._tasks.pop(thread_id, None))

        if start:
            thread.start()

    def start(self, thread_id, payload=None):
        thread:EasyThread = self._tasks.get(thread_id)
        if thread:
            if payload is not None:
                thread.payload = payload
            if not thread.isRunning():
                thread.start()
        else:
            print(f"Task '{thread_id}' not found.")

    def stop(self, thread_id, wait=False):
        thread:EasyThread = self._tasks.get(thread_id)
        if thread and thread.isRunning():
            thread.quit() # 安全退出循环
            if wait:
                thread.wait()
            else:
                # 如果任务不支持 quit (没有事件循环)，强行结束
                thread.terminate() 
            self._tasks.pop(thread_id, None)

    def stop_all(self, wait=False):
        for tid in list(self._tasks.keys()):
            self.stop(tid, wait)

    def has(self, thread_id):
        return thread_id in self._tasks
    
    def remove(self, thread_id=None, wait=False):
        if thread_id is None:
            self.stop_all(wait)
            self._tasks.clear()
            return

        if thread_id in self._tasks:
            self.stop(thread_id, wait)
            self._tasks.pop(thread_id)