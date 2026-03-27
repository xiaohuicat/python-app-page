from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QWidget, QLayout, QVBoxLayout

from app_page_core import Callback
from ..animation.Shadow import Shadow
from ..animation.MoveWin import MoveWin
from ..animation.FadeEffect import FadeEffect
from ..utils import assetsRead, assetsUrl
from .WidgetManager import WidgetManager

# ====================== UI模板定义 ======================
create_template = lambda main_content: '''
<% title_class = 'light' if title == '' else '' %>
<template>
    <div class="container" width="${_width}" height="${_height}" size_policy="True">
        <v-box margins="[10,10,10,10]" spacing="0">
            <!-- 头部区域 -->
            <div id="header" class="header" height="${_header_height}">
                <h-box spacing="10" margins="${_header_margins}" align="AlignTop">
                    <!-- 标题编辑框 -->
                    <line-edit id="title_edit" height="24" visible="false" text="${_title}"/>
                    <!-- 标题显示按钮 -->
                    <button id="title" height="24" text="${_display_title}" class="${title_class}"/>
                    <!-- 关闭按钮 -->
                    <button id="btn_close" width="24" height="24" />
                </h-box>
            </div>
            <!-- 主体内容区域 -->
            ''' + main_content + '''
            <div />
        </v-box>
    </div>
</template>
'''

create_style = lambda radius: '''
.container {
    background-color: #ffffff;
    border-radius: '''+ str(radius) +''';
}
.header {
    border: none;
}
#title {
    color: #333;
    font-size: 20px;
    font-weight: bold;
    border: none;
}
#title.light {
    color: #888;
}
#title_edit {
    font-size: 20px;
    font-weight: bold;
    color: #4682B4;
    border: none;
    text-align: center;
}
#btn_close {
    color: #333;
    font-size: 22px;
    border: none;
    border-radius: 5px;
    padding: 3px;
    image: url("''' + assetsUrl('icon', 'close_black.png') + '''");
}
#btn_close:hover {
    background-color: #f0f0f0;
}
'''

# ====================== 核心类定义 ======================
class CallPanel(QDialog):
    # 可选：定义信号供外部使用
    title_changed = Signal(str)
    
    def __init__(self, main_template: str, main_params: dict, style_sheet: str = '', options: dict = {}):
        """
        弹窗面板初始化
        
        参数说明:
            main_template: str
                面板渲染使用的模板字符串，用于动态生成面板内容
            main_params: dict
                渲染模板时所需的参数字典，键值对形式传递模板变量
            style_sheet: str, optional
                面板的样式表字符串，用于自定义UI样式，默认值为空字符串
            options: dict, optional
                面板的额外配置选项字典，如窗口大小、位置、行为等，默认值为空字典
        """
        super().__init__()
        # 基础属性初始化
        self.callback = Callback()
        self.main_template = main_template if isinstance(main_template, str) else ''
        self.main_params = main_params if isinstance(main_params, dict) else {}
        self.style_sheet = style_sheet if isinstance(style_sheet, str) else ''
        self.options = options if isinstance(options, dict) else {}

        # 动画效果
        self.fade_effect = FadeEffect(self, 100)
        
        # 1. 窗口基础设置（整合所有配置逻辑）
        self._init_window()
        
        # 2. 渲染UI
        self._render_ui()
        
        # 3. 绑定事件
        self._handle_register()

    # ====================== 核心初始化方法 ======================
    def _init_window(self):
        """初始化窗口基础属性（整合所有配置逻辑）"""
        # 清理旧布局
        if self.layout() is not None:
            old_layout = self.layout()
            QWidget().setLayout(old_layout)
            old_layout.deleteLater()
        
        # 创建UI挂载节点
        self.ui = QWidget()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.ui)
        self.setLayout(main_layout)
        [a, b, c, d] = self.options.get('margins', [10, 10, 10, 10])
        self.setContentsMargins(10, 10, 10, 10)

        # 窗口尺寸设置
        width = self.options.get('width', 400) + (a + c)
        height = self.options.get('height', 600) + (b + d)
        self.setFixedWidth(width)
        self.setFixedHeight(height)

        # 1. 透明窗口配置
        if self.options.get('frameless', True):
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)

        # 2. 置顶配置
        if self.options.get('always_on_top', True):
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 3. 标题配置
        topic = self.options.get('topic', self.options.get('title', ''))
        self.setWindowTitle(topic)

        # 6. 阴影效果配置
        if self.options.get('shadow', True):
            Shadow(self.ui)
        
        # 7. 可移动配置
        if self.options.get('movable', True):
            MoveWin(self, self.options.get('id', None))

    def _render_ui(self):
        """渲染UI模板并初始化Widget控制器"""
        # 渲染UI模板
        title = self.options.get('title', '')
        self.widgets_controller: WidgetManager = WidgetManager(
            self.ui, 
            create_template(self.main_template), 
            {
                '_width': self.options.get('width', 400),
                '_height': self.options.get('height', 600),
                '_header_height': self.options.get('header_height', 30),
                '_header_margins': self.options.get('header_margins', [0,0,0,0]),
                '_title': title,
                '_display_title': title if title else "请输入标题",
                **self.main_params,
            }
        )
        # 设置样式
        panel_radius = self.options.get('radius', 10)
        radius = panel_radius if isinstance(panel_radius, int) else 10
        self.ui.setStyleSheet(assetsRead('style.qss') + create_style(radius) + self.style_sheet)

        # 缓存常用控件
        self.title_btn = self.getWidget('title')
        self.title_edit = self.getWidget('title_edit')
        self.btn_close = self.getWidget('btn_close')

    def _handle_register(self):
        self.register('title', 'clicked', self._title_click)
        self.register('btn_close', 'clicked', self.fade_effect.close)
        self.register('title_edit', 'textChanged', self._refresh_title)
        self.register('title_edit', 'returnPressed', self._title_edit_finish)
        self.title_edit.focusOutEvent = self._title_edit_finish

    # ====================== 对外暴露的核心方法 ======================
    def register(self, id: str, signal: str, callback):
        """统一的事件注册方法"""
        self.widgets_controller.register(id, signal, callback)

    def getWidget(self, id: str) -> QWidget | QLayout:
        """获取指定ID的控件"""
        return self.widgets_controller.getWidget(id)
    
    def setClass(self, id: str, className: str):
        """设置类名"""
        return self.widgets_controller.setClass(id, className)

    def showPanel(self, is_exec=False):
        """支持带动画打开面板"""
        self.fade_effect.show(is_exec)

    # ====================== 业务逻辑方法 ======================
    def _title_click(self):
        """标题点击进入编辑状态"""
        if not self.options.get('editable_title', False):
            return
        
        self.title_btn.setVisible(False)
        self.title_edit.setVisible(True)
        self.title_edit.setFocus()

    def _title_edit_finish(self, event=None):
        """标题编辑完成"""
        print("title退出编辑状态")
        self.title_edit.setVisible(False)
        self.title_btn.setVisible(True)
        
        title_val = self.title_edit.text().strip()
        self.setClass('title', "" if title_val else "light")

        # 触发标题变更信号
        self.title_changed.emit(title_val)

    def _fade_close_panel(self):
        """关闭面板（带动画）"""
        if hasattr(self, "callback"):
            self.callback.run("before_close")
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
        # 清理Widget控制器
        if hasattr(self, "widgets_controller"):
            self.widgets_controller.destroy()
        self.main_template = None
        self.style_sheet = None
        self.deleteLater()