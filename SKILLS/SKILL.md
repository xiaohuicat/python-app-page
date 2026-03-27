# 页面对象
Page对象是创建和管理页面的关键对象。它控制页面的渲染，通过id获取组件，注册事件，设置class，进行页面跳转等并内置了数据存取的方法，可以快速开发页面。以下是一个简单的使用，基于这个案例进行深入的介绍。

```python
from app_page import Page

# 模版支持moka语法，接受setup返回词典中的变量
template = """
<template>
  <div>
    <v-box>
      <label text="${title}" class="title" />
      <text-edit id="editor" class="edit-content" text="${content}" />
    </v-box>
  </div>
</template>
"""
style = """
.title {
  color: #333;
  font-size: 20px;
}
#editor {
  color: #333;
  padding: 10px;
  font-size: 16px;
  border-radius: 10px;
  background-color: #e0e0e0;
}
"""

# 定义编辑页面
class Editor(Page):
  def __init__(self):
    # 初始化添加名称自动生成持久化对象，可通过self.localStore访问
    super().__init__("editor")
    self.template = template
    self.style = style

  def setup(self) -> dict:
    # 此处返回的变量可在moka模版中使用
    return {'title': '编辑器'}

  def show(self, *args):
    # 获取持久化编辑内容
    content = self.localStore.get("editor-value", '')
    # 根据id获取标签渲染组件并设置内容
    self.getWidget("editor").setPlainText(content)
    # 注册事件，(id，事件类型，回调函数)
    self.register("editor", 'textChanged', lambda *args: self.textChange())

  # 值改变更新到持久化内容
  def textChange(self):
    self.localStore.set("editor-value", self.getWidget("editor").toPlainText())
```

### 1、 编写xml模版。
支持moka语法，如下：

```python
template = """
<template>
  <div class="container" height="250">
    <v-box>
      <label text="${title}" class="title" />
      <text-edit id="editor" class="edit-content" />
      <button id="help" text="${button_text}" height="32" width="100" class="button" />
    </v-box>
  </div>
</template>
"""
```
title和button_text变量，通过页面对象Page的setup方法中返回一个词典传递。div是QWidget组件，如果内部需要添加元素则先添加一个布局，如以上的v-box，支持v-box和h-box，分别对应垂直布局和水平布局。框架内置了组件别名简化模版的编写，如下所示：

```python
# 组件类型别名映射
aliasWidgetMap = {
  # 基础组件
  'div': 'QWidget',
  'widget': 'QWidget',
  'label': 'QLabel',
  'button': 'QPushButton',
  'line-edit': 'QLineEdit',
  'text-edit': 'QPlainTextEdit',
  'selector': 'QComboBox',
  'checkbox': 'QCheckBox',
  'radio': 'QRadioButton',
  # 布局相关
  'grid': 'QGridLayout',
  'h-box': 'QHBoxLayout',
  'v-box': 'QVBoxLayout',
  'form': 'QFormLayout',
  'stacked': 'QStackedLayout',
  'graphics-anchor': 'QGraphicsAnchorLayout',
  'graphics-grid': 'QGraphicsGridLayout',
  'graphics-layout': 'QGraphicsLayout',
  'graphics-linear': 'QGraphicsLinearLayout',
}
```

组件是属性支持如下：
- id 组件id，可以通过getWidget获取组件对象
- text 组件文本
- title 组件标题，鼠标悬停暂时
- style 设置组件样式
- margins 组件外间距
- spacing 组件内间距
- width 组件宽度
- height 组件高度
- disabled 禁用
- visible 显示，可用于隐藏组件
- placeholder 占位符
- password 密码
- align 文本对齐方式，AlignCenter、AlignLeft、AlignRight、AlignTop、AlignBottom
- scroll 滚动
- options 组件选项，仅支持QComboBox组件，传入下拉选项
- shadow 给添加阴影，值为阴影配置项，支持offset、radius、color
- children 添加子组件
- event-filter 事件过滤器
- size-policy 组件大小策略

### 2、编写qss样式。
样式必须为qss合法样式，可参考[qss样式](https://doc.qt.io/qt-5/stylesheet-examples.html)
选择器可以是class或id，如下：

```qss
.container {
  color: #333;
  border-radius: 10px;
}
#editor {
  color: #333;
  padding: 10px;
}
```
这个样式表的内容在页面渲染时会自动添加到跟组件中。

### 3、传递变量到模板
通过setup方法返回变量，可被模版使用。由于模版必须是合法的xml，对于输入文本避免出现不合法字符，建议使用encode函数转义，模板编译的时会自动还原为原来的文本。
```python
from app_page.utils import encode

# setup函数内返回变量
setup_return_dict = {
  'title': '编辑器',
  'content': encode(self.localStore.get("editor-value", '')),
}
```

### 4、获取存储本地的数据
存储数据可参考如下代码：
```python
# 获取数据
self.localStore.get("key", "default")
# 设置数据
self.localStore.set("key", "value")
# 立即保存，此方法默认值页面隐藏时调用
self.localStore.save()
```

### 5、获取全局数据
全局数据可参考如下代码：
```python
# 获取数据
self.store.get("key", "default")
# 设置数据
self.store.set("key", "value")
```

### 6、获取组件
获取组件可参考如下代码：
```python
self.getWidget("id")
```

### 7、注册事件
注册事件可参考如下代码：
```python
# 参数分别是id，信号类型，回调函数
self.register("id", "clicked", callback)
```

### 8、设置类
设置类可参考如下代码：
```python
self.setClass("id", "class")
```

## 小结
之所以Page对象支持以上方法是初始化的时候进行了模板的解析和渲染。其原理如下：
```python
from app_page import WidgetManager
# 组件的管理
widgetManager:WidgetManager = WidgetManager(self.ui, template, {})
```
widgetsController对象提供了以下方法：
- getWidget(id) 获取组件对象
- register(id, event, callback) 注册事件
- setClass(id, class) 设置class
- setIcon(id, icon) 设置icon
- setText(id, text) 设置text
- getText(id) 获取text
- destroy() 销毁所有组件，Page对象隐藏时自动调用

用户在自定义页面开发时，可参考以上方法，实现页面功能。

# 弹窗面板
弹窗面板和页面对象类似。
```python
from app_page import CallPanel
# 创建弹窗面板
panel = CallPanel(
  # 不需要添加template标签，其余的和页面对象的一样
  main_template=main_template,
  # 模版参数，和页面对象一样
  main_params=main_params,
  # 样式，和页面对象一样
  style_sheet=main_style,
  # 弹窗配置参数
  options=options
)
# 显示弹窗
panel.showPanel()
```
panel弹窗实例化对象支持register，getWidget，setClass方法。
弹窗的配置参数，options:
- id: 弹窗id
- title: 弹窗标题
- width: 弹窗宽度，默认400
- height: 弹窗高度，默认600
- frameless: 是否无边框，默认True
- always_on_top: 是否置顶，默认True
- topic: 主题，用于设置弹窗的title，没有主题时默认使用title值
- shadow: 是否显示阴影，默认True
- movable: 是否允许移动，默认True
- radius: 弹窗圆角，默认10

开发的时候和默认值一致，建议不填。