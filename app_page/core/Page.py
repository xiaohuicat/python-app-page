import time
from typing import Optional, Callable, Dict, Any, List
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QLayout, QVBoxLayout,
    QHBoxLayout, QGridLayout
)
from nanoid import generate

# 自定义模块导入（保持原有结构）
from app_page_core import Callback, Children, Param, Store
from ..core.Tips import Tips
from ..core.TipsBox import TipsBox
from ..core.PageManager import PageManager
from ..core.Thread import ThreadManager
from ..core.Setting import getSetting
from ..core.render import render
from ..core.WidgetsController import WidgetsController
from ..utils import layout_clear, blur_image
from ..MainWindow import MainWindow


class Page:
    """
    基于PySide6的页面管理基类
    提供页面生命周期、渲染、事件、异步任务等核心能力
    """
    def __init__(self, name: Optional[str] = None) -> None:
        # 基础标识属性
        self.name: Optional[str] = name
        self.id: str = generate(size=10)
        self.status: str = 'hide'
        
        # 核心管理对象
        self.callback: Callback = Callback()                     # 回调函数管理
        self.children: Children = Children()                     # 子页面管理
        self.store: Store = Store()                              # 全局存储
        self.pageParam: Param = Param()                          # 页面参数

        # 外部依赖对象（通过注入方式赋值）
        self.app: Optional[QApplication] = None
        self.root: Optional['Page'] = None
        self.mainWin: Optional[MainWindow] = None
        self.pageManager: Optional[PageManager] = None
        self.threadManager: Optional[ThreadManager] = None
        self.param: Optional[Param] = None

        # 模板与样式
        self.template: str = "<template></template>"
        self.style: str = ""
        self.playMedia: Optional[Callable] = None

        # 私有核心对象
        self.__widgetsController: WidgetsController = WidgetsController()  # 组件控制器
        self.__global_data: Dict[str, Any] = {}                            # 页面全局数据
        self.__parent: Optional[QWidget] = None                            # 父容器
        self.__layout: Optional[QLayout] = None                            # 布局管理器
        self._tips_box: Optional[TipsBox] = None                           # 提示框实例

        # 本地存储初始化（优化版）
        self.localStore: Optional[Param] = None
        if name:
            path = self.getSoftwarePath("userPath", f"pages/{name}/config.json")
            self.localStore = Param(path, {})
            if getSetting("IS_DEBUG"):
                print(f"页面 {name} 的本地存储路径为: {path}")

    def setup(self) -> Optional[Dict[str, Any]]:
        """页面初始化钩子"""
        return None

    def rerender(self, params: Dict[str, Any]) -> None:
        """
        重新渲染页面
        :param params: 传递给模板的渲染参数
        """
        # 校验模板有效性
        if not hasattr(self, 'template') or not self.template.strip():
            if getSetting('IS_DEBUG'):
                print(f"页面 {self.name or self.id} 无有效模板，跳过渲染")
            return

        if getSetting('IS_DEBUG'):
            print('[传递给模板的变量]', params)

        # 1. 清理旧内容（仅执行一次）
        self.hideBefore()

        # 2. 确保父容器和布局存在
        if not self.getParent():
            self.setParent(QWidget())
        if not self.getLayout():
            self.setLayout('v-box')

        # 3. 配置布局样式
        layout = self.getLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 4. 应用页面样式
        if self.style:
            self.getParent().setStyleSheet(self.style)

        # 5. 模板渲染与组件挂载
        template_params = params if isinstance(params, dict) else {}
        render_result = render(layout, self.template, template_params)
        self.__widgetsController.setWidgets(render_result['widgets'])
        self.__widgetsController.setWidgetList(render_result['allWidgets'])

    def show(self, *args) -> None:
        """显示页面"""
        print("显示页面:", self.name or self.id, "参数:", args)
        self.setStatus('show')

    def hide(self, *args) -> None:
        """隐藏页面"""
        print("隐藏页面:", self.name or self.id, "参数:", args)
        self.setStatus('hide')

    def hideBefore(self) -> None:
        """页面隐藏前的清理工作"""
        # 清理布局
        if self.__layout:
            layout_clear(self.__layout)
            self.__layout = None

        # 销毁组件管理器
        if self.__widgetsController:
            self.__widgetsController.destroy()

        # 清理子页面和回调
        if self.children:
            self.children.remove()
        if self.callback:
            self.callback.clear()

        # 保存本地存储数据
        if self.localStore:
            self.localStore.save()

    def destroy(self) -> None:
        """销毁页面，释放所有资源"""
        try:
            # 标记状态并执行基础清理
            self.status = 'hide'
            self.hideBefore()
            self.hide()

            # 销毁组件控制器
            self.__widgetsController = None

            # 清理本地存储
            if self.localStore:
                self.localStore.clear()
                self.localStore = None

            # 移除全局事件过滤器（带异常保护）
            try:
                app_callback: Optional[Callback] = self.store.get('APP_CALLBACK')
                if app_callback:
                    app_callback.remove('event-filter')
            except Exception as e:
                if getSetting('IS_DEBUG'):
                    print(f"移除全局事件过滤器失败: {e}")

            # 清理页面参数
            if self.pageParam:
                self.pageParam.clear()
                self.pageParam = None

            # 执行全局数据销毁回调
            destroy_callback = self.getGlobal('__destroy')
            if callable(destroy_callback):
                try:
                    destroy_callback()
                except Exception as e:
                    if getSetting('IS_DEBUG'):
                        print(f"全局销毁回调执行失败: {e}")

            # 清空全局数据
            self.setGlobal({})

            # 清空引用，帮助GC回收
            self.children = None
            self.callback = None
            self.template = None
            self.__parent = None
            self._tips_box = None

        except Exception as e:
            if getSetting('IS_DEBUG'):
                print(f"页面 {self.name or self.id} 销毁失败: {e}")

    def register(self, id: str, signal: str, callback: Callable) -> None:
        """
        注册组件事件
        :param id: 组件ID
        :param signal: 信号名称
        :param callback: 回调函数
        """
        self.__widgetsController.register(id, signal, callback)

    def regist_filter(self, callback: Callable) -> None:
        """注册全局事件过滤器"""
        app_callback: Callback = self.store.get('APP_CALLBACK')
        app_callback.remove('event-filter')
        app_callback.add('event-filter', callback)

    def navigateTo(self, page_id: str, *args) -> None:
        """
        导航到指定页面
        :param page_id: 目标页面ID
        :param args: 页面参数
        """
        if self.pageManager:
            self.pageManager.open(*(page_id, *args))
        else:
            if getSetting('IS_DEBUG'):
                print("页面管理器未初始化，无法导航")

    def setTimeout(self, callback: Callable, seconds: float, *args, **kwargs) -> Optional[str]:
        """
        设置定时器
        :param callback: 回调函数
        :param seconds: 延迟秒数
        :param args: 回调函数位置参数
        :param kwargs: 回调函数关键字参数
        :return: 线程ID（用于取消定时器）
        """
        if not self.threadManager:
            if getSetting('IS_DEBUG'):
                print("线程管理器未初始化，无法创建定时器")
            return None

        # 生成唯一线程ID
        thread_id = f"timeout_{self.id}_{generate(size=6)}"

        def wrapper(*args) -> None:
            """定时器包装函数（带异常处理和参数传递）"""
            try:
                callback(*args, **kwargs)
            except Exception as e:
                if getSetting('IS_DEBUG'):
                    print(f"定时器 {thread_id} 回调执行失败: {e}")
            finally:
                self.threadManager.remove(thread_id)

        # 添加线程任务
        self.threadManager.add({
            "id": thread_id,
            "callback": wrapper,
            "function": lambda: time.sleep(seconds)
        }, True)

        return thread_id

    def clearTimeout(self, thread_id: str) -> None:
        """
        清除定时器
        :param thread_id: 定时器线程ID
        """
        if self.threadManager:
            self.threadManager.remove(thread_id)

    def async_run(self, function: Callable, callback: Optional[Callable] = None, *args, **kwargs) -> Optional[str]:
        """
        异步执行函数
        :param function: 异步执行的函数
        :param callback: 执行完成后的回调函数
        :param args: 异步函数位置参数
        :param kwargs: 异步函数关键字参数
        :return: 线程ID
        """
        if not self.threadManager:
            if getSetting('IS_DEBUG'):
                print("线程管理器未初始化，无法执行异步任务")
            return None

        # 生成唯一线程ID
        thread_id = f"async_{self.id}_{generate(size=6)}"

        def wrapper(*args) -> None:
            """异步任务包装函数"""
            try:
                if callable(callback):
                    callback(*args)
            except Exception as e:
                if getSetting('IS_DEBUG'):
                    print(f"异步任务 {thread_id} 执行失败: {e}")
            finally:
                self.threadManager.remove(thread_id)

        # 添加线程任务
        self.threadManager.add({
            "id": thread_id,
            "callback": wrapper,
            "function": lambda: function(*args, **kwargs)
        }, True)

        return thread_id

    def tips(self, msg: str, type: str = 'default') -> None:
        """
        显示提示信息
        :param msg: 提示内容
        :param type: 提示类型（default/success/error等）
        """
        def _show_tips() -> None:
            """确保在Qt主线程执行UI操作"""
            # 清理旧提示
            if hasattr(self.app, "tips_widget"):
                hook = self.mainWin.win.mouseMoveEventHook
                hook.remove(id="tips")
                self.app.tips_widget.deleteLater()
                delattr(self.app, "tips_widget")

            # 创建新提示
            self.app.tips_widget = Tips(msg, type)
            hook = self.mainWin.win.mouseMoveEventHook
            hook.add(id="tips", func=lambda *args: self.app.tips_widget.center())

        # 确保UI操作在主线程执行
        if self.app and self.app.thread() != self.app.thread():
            self.app.invoke(_show_tips)
        else:
            _show_tips()

    def tipsBox(self,
               topic: str = '',
               title: str = '',
               content: str = '',
               confirm: Optional[Callable] = None,
               cancel: Optional[Callable] = None,
               close: Optional[Callable] = None) -> None:
        """
        显示提示框（修正了原有的cancle拼写错误）
        :param topic: 提示框主题
        :param title: 提示框标题
        :param content: 提示框内容
        :param confirm: 确认按钮回调
        :param cancel: 取消按钮回调
        :param close: 关闭按钮回调
        """
        # 检查是否已有活跃的提示框
        if hasattr(self, "_tips_box") and self._tips_box and not self._tips_box.isHidden():
            if getSetting('IS_DEBUG'):
                print("提示框已存在，请关闭后再打开")
            return

        # 创建提示框实例
        self._tips_box = TipsBox(topic=topic, title=title, content=content)

        def _close() -> None:
            """提示框关闭后的清理逻辑"""
            if self._tips_box:
                self._tips_box.callback.remove()
                self._tips_box.deleteLater()
                self._tips_box = None
                if callable(close):
                    close()

        # 注册按钮回调
        if callable(confirm):
            self._tips_box.callback.add("confirm", confirm)
        if callable(cancel):
            self._tips_box.callback.add("cancel", cancel)
        self._tips_box.callback.add("close", _close)

        # 显示提示框
        self._tips_box.show()

    def setWidgets(self, widgets: Dict[str, QWidget]) -> None:
        """设置组件列表"""
        self.__widgetsController.setWidgets(widgets)

    def getWidget(self, id: Optional[str] = None) -> Optional[QWidget | Dict[str, QWidget]]:
        """
        获取组件实例
        :param id: 组件ID（None时返回所有组件）
        :return: 组件实例或组件字典
        """
        return self.__widgetsController.getWidget(id)

    def setStatus(self, status: str) -> None:
        """设置页面状态"""
        self.status = status

    def getStatus(self) -> str:
        """获取页面状态"""
        return self.status

    def hasGlobal(self, key: str) -> bool:
        """检查全局数据是否存在指定键"""
        return key in self.__global_data

    def getGlobal(self, key: Optional[str] = None, default: Any = None) -> Any:
        """
        获取全局数据
        :param key: 数据键（None时返回所有全局数据）
        :param default: 默认值（当key不存在时返回该值）
        :return: 对应值或全部数据
        """
        if key is None:
            return self.__global_data
        return self.__global_data.get(key, default)

    def setGlobal(self, key: str | Dict[str, Any], value: Optional[Any] = None) -> None:
        """
        设置全局数据
        :param key: 数据键或字典
        :param value: 数据值（key为字典时需为None）
        """
        if isinstance(key, str) and value is not None:
            self.__global_data[key] = value
        elif isinstance(key, dict) and value is None:
            self.__global_data = key
        else:
            raise TypeError("参数错误：key为字符串时value不能为空，或key为字典时value必须为None")

    def onGlobalDestroy(self, callback: Callable) -> None:
        """注册全局数据销毁回调"""
        self.setGlobal('__destroy', callback)

    def getParent(self) -> Optional[QWidget]:
        """获取父容器"""
        return self.__parent

    def setParent(self, parent: Optional[QWidget] = None) -> None:
        """设置父容器"""
        if parent is None:
            self.__parent = QWidget()
        else:
            self.__parent = parent

    def getLayout(self) -> Optional[QLayout]:
        """获取布局管理器"""
        if not self.__layout and self.__parent:
            self.__layout = self.__parent.layout()
        return self.__layout

    def setLayout(self, layoutType: str) -> None:
        """
        设置布局类型
        :param layoutType: 布局类型（v-box/h-box/grid）
        """
        if not self.__parent:
            raise ValueError("请先设置父组件（调用setParent）")

        # 布局类型映射
        layout_map: Dict[str, type[QLayout]] = {
            'v-box': QVBoxLayout,
            'h-box': QHBoxLayout,
            'grid': QGridLayout
        }

        # 校验布局类型
        if layoutType not in layout_map:
            valid_types = list(layout_map.keys())
            raise ValueError(f"不支持的布局类型: {layoutType}，支持类型: {valid_types}")

        # 避免重复创建相同类型布局
        if self.__layout and isinstance(self.__layout, layout_map[layoutType]):
            return

        # 创建布局
        self.__layout = layout_map[layoutType](self.__parent)

    def getSoftwarePath(self, typeName: str, *args) -> str:
        """
        获取软件路径
        :param typeName: 路径类型（userPath/tempPath/systemPath）
        :param args: 路径片段
        :return: 拼接后的路径
        """
        valid_types = ['userPath', 'tempPath', 'systemPath']
        if typeName not in valid_types:
            raise ValueError(f"typeName {typeName} 无效，支持类型: {valid_types}")
        
        if not self.param:
            raise RuntimeError("param对象未初始化，无法拼接路径")
        
        return self.param.pathJoin(typeName, *args)

    def getBlurImage(self, url: str, radius: float = 5, opacity: float = 1) -> str:
        """
        获取模糊处理后的图片路径
        :param url: 原图URL
        :param radius: 模糊半径
        :param opacity: 透明度
        :return: 处理后的图片路径
        """
        folder = self.getSoftwarePath("tempPath", "blur_images")
        return blur_image(folder, url, radius, opacity)

    @property
    def info(self) -> str:
        """获取页面信息"""
        return f"\n当前页面有{len(self.children.components.keys()) if self.children else 0}个子页面。\n" + (
            self.children.info() if self.children else ""
        )

    def __getitem__(self, name: str) -> Any:
        """通过索引方式获取属性（增强容错）"""
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if getSetting('IS_DEBUG'):
                print(f"属性 {name} 不存在")
            return None

    def __getattribute__(self, name: str) -> Any:
        """优先从store获取属性，增强异常保护"""
        try:
            # 避免递归调用
            store = super().__getattribute__('store')
            if store and store.has(name):
                return store.get(name)
            return super().__getattribute__(name)
        except:
            # 当store未初始化时直接返回实例属性
            return super().__getattribute__(name)

    def __del__(self) -> None:
        """析构函数，确保资源最终释放"""
        if getSetting('IS_DEBUG'):
            print(f"页面 {self.name or self.id} 开始析构")
        self.destroy()


# 类型别名（方便后续扩展）
PageType = Page