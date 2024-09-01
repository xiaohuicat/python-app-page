# Python app framework

# Installation
```shell
pip install app-page
```
# Page页面属性
callback   回调管理对象
children   子页面管理对象
store      全局变量管理对象

# Usage
应用首页，初始化全局对象，页面对象，加载页面
app.py
```python
from app-page import Store, Page

def signal_slots_func(signal, id, func):
  # 绑定信号与槽函数
  print(signal, id, func)

# 初始化全局对象
Store({
  "version": "1.0.0",
  "isLogin": False,
  "functions": {
    # 信号与槽绑定函数"__signal_slots_func"
    "__signal_slots_func": signal_slots_func,
  },
})

# 初始化页面对象
page = Page()
page.setup('app.json')
```
配置页面结构
app.json
```json
{
  "name": "main",
  "id": "id001",
  "style": "app.css",
  "children": "children/page.json",
  "events": {
    "clicked": {
      "btn1": "sendMessage",
      "btn2": "cancel"
    }
  },
  "functions": {
    "sendMessage": "functions/sendMessage.py",
    "cancel": "functions/cancel.py"
  }
}
```