import os
from PySide6.QtCore import Signal, Qt, QSize, QPoint, QEvent, QTimer
from PySide6.QtWidgets import QMainWindow, QWidget, QLayout, QLabel, QHBoxLayout
from PySide6.QtGui import QPixmap, QGuiApplication
from ..core.render.render_main import render
from ..core import WidgetsController
from ..animation import MoveWin, Shadow
from ..utils import assetsUrl


# 界面布局模板
template = '''
<template>
    <div id="main-ui" class="container" width="960" height="700">
        <v-box margins="[0,0,0,0]" spacing="0">
            <div id="header" class="header" height="42">
                <h-box spacing="5" margins="[6,0,6,0]">
                    <button id="btn_left" height="28" width="28" class="btn_left"/>
                    <button id="btn_right" height="28" width="28" class="btn_right"/>
                    <button id="btn_list" height="28" width="28" class="btn_list"/>
                    <button id="btn_big" height="28" width="28" class="btn_big"/>
                    <button id="btn_small" height="28" width="28" class="btn_small"/>
                    <div />
                    <button id="btn_mini" height="28" width="28" class="btn_mini"/>
                    <button id="btn_change" height="28" width="28" class="btn_change"/>
                    <button id="btn_close" height="28" width="28" class="btn_close"/>
                </h-box>
            </div>
            <div id="image_container">
                <h-box id="image_layout" align="AlignCenter" margins="[0,0,0,0]" spacing="0">
                    <label id="image" />
                </h-box>
            </div>
        </v-box>
    </div>
</template>
'''

# 界面样式表
show_image_style = lambda:'''
QPushButton {
    font-size: 14px;
    padding: 2px;
    background-color: transparent;
    border-color: transparent;
    border-radius: 4px;
}
QPushButton:hover {
    color: #fff;
    border-color: rgba(0,0,0,0.05);
    background-color: rgba(0,0,0,0.05);
}
.container {
    background-color: #ffffff;
}
.btn_left {
    image: url('''+ assetsUrl('icon', 'image', 'btn_left.png') +''');
}
.btn_left_sleep {
    image: url('''+ assetsUrl('icon', 'image', 'btn_left_sleep.png') +''');
}
.btn_right {
    image: url('''+ assetsUrl('icon', 'image', 'btn_right.png') +''');
}
.btn_right_sleep {
    image: url('''+ assetsUrl('icon', 'image', 'btn_right_sleep.png') +''');
}
.btn_list {
    image: url('''+ assetsUrl('icon', 'image', 'btn_list.png') +''');
}
.btn_big {
    image: url('''+ assetsUrl('icon', 'image', 'btn_big.png') +''');
}
.btn_big_sleep {
    image: url('''+ assetsUrl('icon', 'image', 'btn_big_sleep.png') +''');
}
.btn_small {
    image: url('''+ assetsUrl('icon', 'image', 'btn_small.png') +''');
}
.btn_small_sleep {
    image: url('''+ assetsUrl('icon', 'image', 'btn_small_sleep.png') +''');
}
.btn_mini {
    image: url('''+ assetsUrl('icon', 'image', 'minimizing.png') +''');
}
.btn_change {
    padding: 6px;
    image: url('''+ assetsUrl('icon', 'image', 'btn_change.png') +''');
}
.btn_change_sleep {
    padding: 4px;
    image: url('''+ assetsUrl('icon', 'image', 'btn_change_sleep.png') +''');
}
.btn_close {
    image: url('''+ assetsUrl('icon', 'image', 'btn_close.png') +''');
}
.btn_close:hover {
    background-color: rgba(255, 0, 0, 0.7);
    image: url('''+ assetsUrl('icon', 'close.png') +''');
}
'''

class ShowImage(QMainWindow):
    # 图片切换信号
    image_request = Signal(object)

    def __init__(self, currentPath:str|None = None, images:list|None = None):
        super().__init__()
        # 初始化图片列表与当前索引
        self.images = images if images else []
        self.image_num = len(self.images)
        self.currentPath = currentPath if currentPath else ''
        self.current = self.images.index(self.currentPath) if self.currentPath in self.images else 0

        # 窗口设置：无边框、透明背景、窗口拖动、阴影
        MoveWin(self, "image_window_position")
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 主界面初始化
        self.ui = QWidget()
        self.ui.setStyleSheet(show_image_style())
        self.setCentralWidget(self.ui)
        self.setContentsMargins(10, 10, 10, 10)
        self.setFixedWidth(980)
        self.setFixedHeight(740)
        Shadow(self.ui)

        # 渲染模板并获取控件控制器
        render_dict = render(self.ui, template, {})
        self.widgetsController:WidgetsController = WidgetsController(
            widget_id_map=render_dict['widget_id_map'], 
            widget_list=render_dict['widget_list']
        )
        
        # 获取图片相关控件
        self.image_label: QLabel = self.getWidget('image')
        self.image_container: QWidget = self.getWidget('image_container')
        self.image_layout: QHBoxLayout = self.getWidget('image_layout')
        
        # 按钮绑定事件
        self.register('btn_change', 'clicked', self.restore_or_maximize_window)
        self.register('btn_mini', 'clicked', self.showMinimized)
        self.register('btn_big', 'clicked', self.image_biger)
        self.register('btn_small', 'clicked', self.image_smaller)
        self.register('btn_left', 'clicked', self.left_image)
        self.register('btn_right', 'clicked', self.right_image)
        self.register('btn_close', 'clicked', self.close_page)

        # 基础参数初始化
        self.size = QSize(960, 672)
        self.isMaximized = False
        self.normal_window_rect = None
        self.supported_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff', '.svg'}

        # 图片拖拽变量
        self.is_dragging = False
        self.drag_start_offset = QPoint() 

        # 调整图片层级，启用鼠标追踪与事件过滤
        self.image_layout.removeWidget(self.image_label)
        self.image_label.setParent(self.image_container)
        self.image_label.setMouseTracking(True)
        self.image_label.installEventFilter(self)

        # 加载并显示图片
        if self.has_image():
            self.show_image()

    # 注册控件信号
    def register(self, id:str, signal:str, callback):
        self.widgetsController.register(id, signal, callback)

    # 设置控件样式类
    def setClass(self, id:str, className:str):
        self.widgetsController.setClass(id, className)

    # 根据ID获取控件
    def getWidget(self, id:str) -> QWidget|QLayout:
        return self.widgetsController.getWidget(id)

    # 加载指定文件夹下的所有图片
    def load_images(self, folderPath: str, currentPath: str | None = None):
        folder = folderPath.rstrip('/\\')
        self.images = sorted([
            os.path.join(folder, f) 
            for f in os.listdir(folder) 
            if os.path.splitext(f)[1].lower() in self.supported_extensions
        ])
        self.image_num = len(self.images)
        self.currentPath = currentPath if currentPath else (self.images[0] if self.image_num > 0 else '')
        self.currentPath = self.currentPath.replace('/', '\\')
        self.current = self.images.index(self.currentPath) if self.currentPath in self.images else 0

    # 重置图片到容器居中位置
    def _reset_image_position(self):
        if not self.image_label.pixmap() or self.image_label.pixmap().isNull():
            return
        
        container_rect = self.image_container.contentsRect()
        pix_size = self.image_label.pixmap().size()
        
        center_x = (container_rect.width() - pix_size.width()) // 2
        center_y = (container_rect.height() - pix_size.height()) // 2
        
        self.image_label.resize(pix_size)
        self.image_label.move(center_x, center_y)

    # 事件过滤：处理图片拖拽、缩放
    def eventFilter(self, obj, event):
        if obj == self.image_label:
            if not hasattr(self, 'pix_raw') or not self.pix_raw:
                return super().eventFilter(obj, event)

            # 鼠标按下：开始拖拽
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self.is_dragging = True
                    self.drag_start_offset = event.pos()
                    self.image_label.setCursor(Qt.ClosedHandCursor)
                    return True

            # 鼠标移动：拖拽图片
            elif event.type() == QEvent.MouseMove:
                if self.is_dragging:
                    global_pos = event.globalPos()
                    container_pos = self.image_container.mapFromGlobal(global_pos)
                    new_pos = container_pos - self.drag_start_offset
                    limited_pos = self._limit_image_position(new_pos)
                    self.image_label.move(limited_pos)
                    return True

            # 鼠标松开：结束拖拽
            elif event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    self.is_dragging = False
                    self.image_label.setCursor(Qt.OpenHandCursor)
                    return True

            # 鼠标进入：显示抓手
            elif event.type() == QEvent.Enter:
                self.image_label.setCursor(Qt.OpenHandCursor)
            
            # 鼠标滚轮：缩放图片
            elif event.type() == QEvent.Wheel:
                if event.angleDelta().y() > 0:
                    self.image_biger()
                else:
                    self.image_smaller()
                return True

        return super().eventFilter(obj, event)

    # 限制图片位置，保证部分区域在容器内
    def _limit_image_position(self, pos: QPoint) -> QPoint:
        container_rect = self.image_container.contentsRect()
        img_size = self.image_label.size()
        margin = 20 

        min_x = container_rect.left() - img_size.width() + margin
        max_x = container_rect.right() - margin
        min_y = container_rect.top() - img_size.height() + margin
        max_y = container_rect.bottom() - margin

        new_x = max(min_x, min(pos.x(), max_x))
        new_y = max(min_y, min(pos.y(), max_y))
        
        return QPoint(new_x, new_y)

    # 图片缩放（保持中心点）
    def apply_zoom(self, factor):
        if not self.pix_raw: return
        
        old_size = self.image_label.size()
        old_pos = self.image_label.pos()
        
        new_size = self.size * factor
        # 限制最大/最小尺寸
        if new_size.width() > 5000:
            self.btn_sleep('btn_big')
            return
        if new_size.width() < 100:
            self.btn_sleep('btn_small')
            return
        
        # 应用缩放
        self.size = new_size
        self.pix = self.pix_raw.scaled(self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(self.pix)
        self.image_label.resize(self.pix.size())

        # 保持中心点不变
        diff_w = (old_size.width() - self.image_label.width()) // 2
        diff_h = (old_size.height() - self.image_label.height()) // 2
        
        new_pos = QPoint(old_pos.x() + diff_w, old_pos.y() + diff_h)
        self.image_label.move(self._limit_image_position(new_pos))

    # 放大图片
    def image_biger(self):
        self.apply_zoom(1.2)
        self.btn_wakeUp('btn_small')

    # 缩小图片
    def image_smaller(self):
        self.apply_zoom(0.8)
        self.btn_wakeUp('btn_big')

    # 判断是否有图片可显示
    def has_image(self):
        return isinstance(self.current, int) and self.image_num > 0

    # 显示当前图片
    def show_image(self):
        no_image = self.current == None or self.image_num == 0
        raw_path = self.images[self.current] if not no_image else assetsUrl('image', 'error.png')
        self.setWindowTitle(os.path.basename(raw_path))
        
        # 加载并缩放图片
        self.pix_raw = QPixmap(raw_path)
        self.size = QSize(960, 672) if not no_image else QSize(64, 64)
        self.pix = self.pix_raw.scaled(self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(self.pix)
        self.image_label.resize(self.pix.size())
        
        # 延迟居中并刷新按钮状态
        QTimer.singleShot(30, self._reset_image_position)
        self.show()
        self.update_navigation_buttons()

    # 窗口最大化/还原
    def restore_or_maximize_window(self):
        if self.isMaximized:
            if self.normal_window_rect:
                self.setGeometry(*self.normal_window_rect)
            self.isMaximized = False
            self.setClass('btn_change', 'btn_change')
        else:
            raw = self.geometry()
            self.normal_window_rect = [raw.x(), raw.y(), raw.width(), raw.height()]
            rect = QGuiApplication.primaryScreen().availableGeometry()
            self.setGeometry(rect.x(), rect.y(), rect.width(), rect.height())
            self.isMaximized = True
            self.setClass('btn_change', 'btn_change_sleep')
        
        QTimer.singleShot(100, self._reset_image_position)

    # 上一张图片
    def left_image(self):
        if self.current > 0:
            self.current -= 1
            self.show_image()

    # 下一张图片
    def right_image(self):
        if self.current < self.image_num - 1:
            self.current += 1
            self.show_image()

    # 更新左右按钮可用状态
    def update_navigation_buttons(self):
        if self.image_num <= 1:
            self.btn_sleep('btn_left')
            self.btn_sleep('btn_right')
        elif self.current == 0:
            self.btn_sleep('btn_left')
            self.btn_wakeUp('btn_right')
        elif self.current == self.image_num - 1:
            self.btn_sleep('btn_right')
            self.btn_wakeUp('btn_left')
        else:
            self.btn_wakeUp('btn_left')
            self.btn_wakeUp('btn_right')

    # 按钮置为禁用样式
    def btn_sleep(self, name):
        self.setClass(name, f'{name}_sleep')

    # 按钮恢复正常样式
    def btn_wakeUp(self, name):
        self.setClass(name, name)
    
    # 关闭窗口并释放资源
    def close_page(self):
        self.close()
        self.image_request.emit(None)
        self.widgetsController.destroy()
        self.deleteLater()