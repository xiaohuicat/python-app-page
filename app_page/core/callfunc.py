import sys

# 全局函数调用
global_fn = None

def call_func(fn, *args, **kwargs):
    # 创建一个追踪函数来捕获局部变量
    def trace_calls(frame, event, arg):
        if event == 'return' and frame.f_code.co_name == fn.__name__:
            # 当目标函数即将返回时，获取其局部变量
            global captured_locals
            captured_locals = frame.f_locals.copy()
        return trace_calls
    
    # 注册追踪函数
    sys.settrace(trace_calls)
    # 执行目标函数
    global global_fn
    global_fn = fn
    fn(*args, **kwargs)
    global_fn = None
    # 取消追踪
    sys.settrace(None)
    
    # 返回捕获的局部变量
    return captured_locals


def current_func():
    return global_fn


if __name__ == "__main__":
    def func(name="World"):
        a = 10
        b = "hello"
        c = [1, 2, 3]

    # 调用并获取结果
    print(call_func(func, name="Alice"))
    