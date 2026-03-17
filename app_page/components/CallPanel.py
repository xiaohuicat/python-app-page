from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QWidget, QLayout, QVBoxLayout, QHBoxLayout, QGridLayout

from app_page_core import Param, Callback
from ..animation import MoveWin, Shadow, FadeEffect
from ..utils import setWidgetStyle
from ..core.render.render_main import render
from ..core.WidgetsController import WidgetsController

# ====================== UI模板定义 ======================
template = '''
<template>
    <div id="call-panel-container" class="container" width="400" height="300">
        <v-box margins="[10,10,10,10]" spacing="0">
            <!-- 头部区域 -->
            <div id="head" class="head" height="40">
                <h-box spacing="10" margins="[0,0,0,0]" align="AlignTop">
                    <!-- 标题编辑框 -->
                    <line-edit id="title_edit" height="24" visible="false"/>
                    <!-- 标题显示按钮 -->
                    <button id="title" height="24" />
                    <!-- 关闭按钮 -->
                    <button id="btn_close" width="24" height="24" text="×"/>
                </h-box>
            </div>
            <!-- 主体内容区域 -->
            <div id="main_content" class="main-content">
                <!-- 动态布局区域 -->
            </div>
        </v-box>
    </div>
</template>
'''

base_style = '''
QWidget#call-panel-container {
    background-color: #ffffff;
    border-radius: 8px;
}
QPushButton#title {
    color: #333;
    font-size: 20px;
    font-weight: bold;
    border-image: none;
    background-color: transparent;
}
QPushButton#title[light="true"] {
    color: #888;
}
QLineEdit#title_edit {
    font-size: 20px;
    font-weight: bold;
    color: #4682B4;
    border-image: none;
    background-color: transparent;
    text-align: center;
}
QPushButton#btn_close {
    border-radius: 5px;
    background-color: #f0f0f0;
    font-size: 22px;
    border-image: none;
}
QWidget#head {
    border-image: none;
    background-color: transparent;
}
QWidget#main_content {
    border-image: none;
    background-color: transparent;
}
'''

# ====================== 核心类定义 ======================
class CallPanel(QDialog):
    # 可选：定义信号供外部使用
    title_changed = Signal(str)
    
    def __init__(self, param: Param|None, config: dict):
        super().__init__()
        print("CallPanel初始化...")
        
        # 基础属性初始化
        self.callback = Callback()
        self.param = param
        self.id = None
        self.config = config
        self.mount_list = []
        
        # 动画效果
        self.fadeEffect = FadeEffect(self, 100, self._fade_close_panel)
        
        # 1. 窗口基础设置
        self._init_window_base()
        
        # 2. 渲染UI
        self._render_ui()
        
        # 3. 绑定事件
        self._bind_events()
        
        # 4. 应用配置
        self.setConfig()

    # ====================== 核心初始化方法 ======================
    def _init_window_base(self):
        """初始化窗口基础属性"""
        # 清空默认布局
        self.setLayout(QWidget().layout())
        
        # 创建UI挂载节点
        self.ui_container = QWidget()
        self.ui_container.setStyleSheet(base_style)
        
        # 设置主容器
        main_layout = QWidget().layout() or QLayout()
        if not main_layout:
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.ui_container)
        self.setLayout(main_layout)

    def _render_ui(self):
        """渲染UI模板并初始化Widget控制器"""
        # 渲染UI模板
        render_dict = render(self.ui_container, template, {})
        
        # 初始化Widget控制器（与参考代码保持一致）
        self.widgetsController: WidgetsController = WidgetsController(
            widget_id_map=render_dict['widget_id_map'],
            widget_list=render_dict['widget_list']
        )
        
        # 缓存常用控件
        self.title_btn = self.getWidget('title')
        self.title_edit = self.getWidget('title_edit')
        self.btn_close = self.getWidget('btn_close')
        self.main_content = self.getWidget('main_content')
        self.head_widget = self.getWidget('head')

    def _bind_events(self):
        """统一绑定控件事件"""
        # 标题点击事件
        self.register('title', 'clicked', self._titleClick)
        # 关闭按钮事件
        self.register('btn_close', 'clicked', self.fadeEffect.close)
        self.register('title_edit', 'textChanged', self._refresh_title)
        self.register('title_edit', 'returnPressed', self._title_edit_finish)
        # 标题编辑框事件
        self.title_edit.focusOutEvent = self._title_edit_finish

    # ====================== 对外暴露的核心方法 ======================
    def register(self, widget_id: str, signal: str, callback):
        """统一的事件注册方法（与参考代码风格一致）"""
        self.widgetsController.register(widget_id, signal, callback)

    def getWidget(self, widget_id: str) -> QWidget | QLayout:
        """获取指定ID的控件（与参考代码风格一致）"""
        return self.widgetsController.getWidget(widget_id)

    def setConfig(self):
        """应用配置（重构后更清晰）"""
        config = self.config
        
        # 遍历配置项并应用
        config_handlers = {
            "size_w_h": self._set_window_size,
            "transparent": self._set_transparent,
            "pin_to_top": self._set_always_on_top,
            "id": self._set_widget_id,
            "style": self._set_custom_style,
            "title": self._set_title,
            "main_layout": self._set_main_layout,
            "head_margin": self._set_head_margins,
            "head_height": self._set_head_height,
            "shadow_effect": self._set_shadow,
            "movable": self._set_movable,
            "close_style": self._set_close_btn_style
        }
        
        for key, value in config.items():
            if key in config_handlers:
                config_handlers[key](value)

    def show(self):
        """重写show方法，支持动画和exec模式"""
        print("CallPanel显示...")
        self.fadeEffect.show()
        if self.config.get("exec_", False):
            self.exec()
        else:
            super().show()

    # ====================== 配置处理方法（拆分后更易维护） ======================
    def _set_window_size(self, size: list):
        """设置窗口尺寸"""
        w, h = size
        self.ui_container.setFixedWidth(w)
        self.ui_container.setFixedHeight(h)
        self.setFixedWidth(w + 40)
        self.setFixedHeight(h + 40)

    def _set_transparent(self, enable: bool):
        """设置透明窗口"""
        if enable:
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)

    def _set_always_on_top(self, enable: bool):
        """设置窗口置顶"""
        if enable:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def _set_widget_id(self, widget_id: str):
        """设置窗口ID"""
        self.id = widget_id
        self.setObjectName(widget_id)

    def _set_custom_style(self, style: dict):
        """设置自定义样式"""
        setWidgetStyle(self.ui_container, style)

    def _set_title(self, title_text: str):
        """设置窗口标题"""
        self.setWindowTitle(title_text)
        if self.config.get("title_edit", False):
            self.title_edit.setText(title_text)
            display_text = title_text if title_text else "请输入标题"
            self.title_btn.setText(display_text)
            # 设置标题浅色样式
            if not title_text:
                self.title_btn.setProperty("light", "true")
                self.title_btn.style().unpolish(self.title_btn)
                self.title_btn.style().polish(self.title_btn)

    def _set_main_layout(self, layout_type: str):
        """设置主体布局"""
        layout_mapping = {
            "V": QVBoxLayout,
            "H": QHBoxLayout,
            "G": QGridLayout
        }
        if layout_type in layout_mapping:
            self.layout_main = layout_mapping[layout_type](self.main_content)
            self.layout_main.setContentsMargins(0, 0, 0, 0)

    def _set_head_margins(self, margins: list):
        """设置头部边距"""
        head_layout = self.head_widget.layout()
        if head_layout:
            head_layout.setContentsMargins(*margins)

    def _set_head_height(self, height: int):
        """设置头部高度"""
        self.head_widget.setFixedHeight(height)

    def _set_shadow(self, enable: bool):
        """设置阴影效果"""
        if enable:
            Shadow(self.ui_container)

    def _set_movable(self, enable: bool):
        """设置窗口可移动"""
        if enable and self.param and self.id:
            MoveWin(self, self.param, self.id)

    def _set_close_btn_style(self, style: dict):
        """设置关闭按钮自定义样式"""
        setWidgetStyle(self.btn_close, [CLOSE_STYLE, style])

    # ====================== 业务逻辑方法 ======================
    def _titleClick(self):
        """标题点击进入编辑状态"""
        print("title进入编辑状态")
        self.title_btn.setVisible(False)
        self.title_edit.setVisible(True)
        self.title_edit.setFocus()

    def _title_edit_finish(self, event=None):
        """标题编辑完成"""
        print("title退出编辑状态")
        self.title_edit.setVisible(False)
        self.title_btn.setVisible(True)
        
        title_val = self.title_edit.text().strip()
        # 更新标题样式
        self.title_btn.setProperty("light", "false" if title_val else "true")
        self.title_btn.style().unpolish(self.title_btn)
        self.title_btn.style().polish(self.title_btn)
        
        # 触发标题变更信号
        self.title_changed.emit(title_val)

    def _fade_close_panel(self):
        """关闭面板（带动画）"""
        if hasattr(self, "callback"):
            self.callback.run("before_close")
        if self.param and hasattr(self.param, "save"):
            self.param.save()
        self.close()

    def _refresh_title(self):
        """实时刷新标题显示"""
        new_title = self.title_edit.text().strip()
        display_text = new_title if new_title else "请输入标题"
        self.title_btn.setText(display_text)
        
        # 触发回调和信号
        if hasattr(self, "callback"):
            self.callback.run("refresh_title", new_title)
        self.title_changed.emit(new_title)

    def destroy(self):
        """销毁面板"""
        self._fade_close_panel()
        # 清理Widget控制器（与参考代码风格一致）
        if hasattr(self, "widgetsController"):
            self.widgetsController.destroy()
        self.deleteLater()

CLOSE_STYLE = {
  "border-radius": "5px",
  "background-color": "#f0f0f0",
  "font-size": "22px",
  "border-image": "None"
}