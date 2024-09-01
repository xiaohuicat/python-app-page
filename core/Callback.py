from collections import defaultdict

class Callback:
    def __init__(self):
        self.callback_dict = defaultdict(list)

    # 添加回调函数
    def add(self, name: str, function):
        self.callback_dict[name].append(function)

    # 获取回调函数
    def get(self, name):
        return self.callback_dict.get(name, [])

    # 运行回调函数
    def run(self, name, *args):
        result = []
        for callback in self.get(name):
            result.append(callback(*args) if args else callback())
        return result

    # 移除回调函数
    def remove(self, name=None):
        if name is None:
            self.callback_dict.clear()
        elif name in self.callback_dict:
            del self.callback_dict[name]

    # 销毁回调管理对象
    def destroy(self):
        self.callback_dict.clear()