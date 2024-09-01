import time

# 毫秒级时间戳
def timestamp():
    return int(time.time() * 1000)

# 事件钩子
class EventHook:
    def __init__(self, delay_ms=10):
        self.pool = {}
        self.delay_ms = delay_ms  # 防抖触发，默认10ms
    
    def add(self, id:str, func:callable):
        self.pool[id] = {
            "func": func,
            "last_run_time": 0  # 初始化上次运行时间为0
        }

    def get(self, id):
        return self.pool.get(id)

    def remove(self, id=None):
        if id is None:
            self.pool.clear()
        else:
            self.pool.pop(id, None)
        return True

    def run(self, *args, **kwargs):
        now = timestamp()
        for id, item in self.pool.items():
            last_run_time = item["last_run_time"]
            if now - last_run_time > self.delay_ms:
                try:
                    item["func"](*args, **kwargs)
                    self.pool[id]["last_run_time"] = now
                except Exception as e:
                    print(f"运行函数失败，ID: {id}，错误: {e}")