import time
from typing import Callable, Any, Dict, Optional

class EventHook:
    def __init__(self, interval_ms: int = 10):
        self._pool: Dict[str, Dict[str, Any]] = {}
        self.interval_ms = interval_ms

    def register(self, hook_id: str):
        """装饰器：更方便地注册函数"""
        def wrapper(func: Callable):
            self.add(hook_id, func)
            return func
        return wrapper

    def add(self, hook_id: str, func: Callable):
        self._pool[hook_id] = {
            "func": func,
            "last_run": 0
        }

    def remove(self, hook_id: Optional[str] = None):
        if hook_id is None:
            self._pool.clear()
        else:
            self._pool.pop(hook_id, None)

    def emit(self, hook_id: Optional[str] = None, *args, **kwargs):
        """
        触发事件。
        :param hook_id: 如果指定 ID，则只触发该事件；否则触发全部。
        """
        now = int(time.time() * 1000)
        
        # 确定需要检查的任务列表
        targets = [hook_id] if hook_id in self._pool else (self._pool.keys() if hook_id is None else [])

        for _id in list(targets):  # 使用 list 包裹防止字典在迭代时改变
            item = self._pool.get(_id)
            if not item:
                continue
            
            if now - item["last_run"] >= self.interval_ms:
                try:
                    item["func"](*args, **kwargs)
                    item["last_run"] = now # 更新执行时间
                except Exception as e:
                    print(f"[EventHook] ID: {_id} execution failed: {e}")