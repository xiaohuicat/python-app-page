import os
from PySide6.QtCore import Signal, Qt, QSize, QPoint, QEvent, QTimer
from PySide6.QtWidgets import QMainWindow, QWidget, QLayout, QLabel, QHBoxLayout
from PySide6.QtGui import QPixmap, QGuiApplication
from ..core.render.render_main import render
from ..core import WidgetsController
from ..core.Device import getScreenInfo
from ..animation import MoveWin, Shadow
from ..utils import assetsUrl


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
                    <div/>
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
'''

class ShowImage(QMainWindow):
    image_request = Signal(object)

    def __init__(self, savePath: str, currentPath: str):
        super().__init__()

        MoveWin(self, "image_window_position")
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.ui = QWidget()
        self.ui.setStyleSheet(show_image_style())
        self.setCentralWidget(self.ui)

        self.setContentsMargins(10, 10, 10, 10)
        self.setFixedWidth(980)
        self.setFixedHeight(740)
        Shadow(self.ui)

        render_dict = render(self.ui, template, {})
        self.widgetsController:WidgetsController = WidgetsController(
            widget_id_map=render_dict['widget_id_map'], 
            widget_list=render_dict['widget_list'])
        
        self.image_label: QLabel = self.getWidget('image')
        self.image_container: QWidget = self.getWidget('image_container')
        self.image_layout: QHBoxLayout = self.getWidget('image_layout')
        
        self.register('btn_change', 'clicked', self.restore_or_maximize_window)
        self.register('btn_big', 'clicked', self.image_biger)
        self.register('btn_small', 'clicked', self.image_smaller)
        self.register('btn_left', 'clicked', self.left_image)
        self.register('btn_right', 'clicked', self.right_image)
        self.register('btn_close', 'clicked', self.close_page)

        self.savePath = savePath.rstrip('/\\')
        self.currentPath = currentPath
        self.size = QSize(960, 672)
        self.isMaximized = False
        self.normal_window_rect = None
        self.screen = getScreenInfo()
        self.supported_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff', '.svg'}

        self.refresh_file_list()
        self.locate_current_image()

        # 拖拽变量
        self.is_dragging = False
        self.drag_start_offset = QPoint() 

        # 初始化图片层级关系
        self.image_layout.removeWidget(self.image_label)
        self.image_label.setParent(self.image_container)
        self.image_label.setMouseTracking(True)
        self.image_label.installEventFilter(self)

        self.show_image()
        self.update_navigation_buttons()

    def register(self, id:str, signal:str, callback):
        self.widgetsController.register(id, signal, callback)

    def setClass(self, id:str, className:str):
        self.widgetsController.setClass(id, className)

    def getWidget(self, id:str) -> QWidget|QLayout:
        return self.widgetsController.getWidget(id)

    def _reset_image_position(self):
        """重置图片位置为容器居中"""
        if not self.image_label.pixmap() or self.image_label.pixmap().isNull():
            return
        
        container_rect = self.image_container.contentsRect()
        pix_size = self.image_label.pixmap().size()
        
        center_x = (container_rect.width() - pix_size.width()) // 2
        center_y = (container_rect.height() - pix_size.height()) // 2
        
        self.image_label.resize(pix_size)
        self.image_label.move(center_x, center_y)

    def eventFilter(self, obj, event):
        if obj == self.image_label:
            if not hasattr(self, 'pix_raw') or not self.pix_raw:
                return super().eventFilter(obj, event)

            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self.is_dragging = True
                    # 记录点击位置相对于图片左上角的偏移
                    self.drag_start_offset = event.pos()
                    self.image_label.setCursor(Qt.ClosedHandCursor)
                    return True

            elif event.type() == QEvent.MouseMove:
                if self.is_dragging:
                    # 将全局坐标转换为容器内的相对坐标，并减去点击时的偏移
                    global_pos = event.globalPos()
                    container_pos = self.image_container.mapFromGlobal(global_pos)
                    new_pos = container_pos - self.drag_start_offset
                    
                    # 限制位置
                    limited_pos = self._limit_image_position(new_pos)
                    self.image_label.move(limited_pos)
                    return True

            elif event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    self.is_dragging = False
                    self.image_label.setCursor(Qt.OpenHandCursor)
                    return True

            elif event.type() == QEvent.Enter:
                self.image_label.setCursor(Qt.OpenHandCursor)
            
            # 滚轮缩放支持 (可选增加)
            elif event.type() == QEvent.Wheel:
                if event.angleDelta().y() > 0:
                    self.image_biger()
                else:
                    self.image_smaller()
                return True

        return super().eventFilter(obj, event)

    def _limit_image_position(self, pos: QPoint) -> QPoint:
        """确保图片至少有10px留在容器可见区域内"""
        container_rect = self.image_container.contentsRect()
        img_size = self.image_label.size()
        margin = 20 # 留存边距

        # X轴限制：左边缘不能超过右边界-margin，右边缘不能小于左边界+margin
        min_x = container_rect.left() - img_size.width() + margin
        max_x = container_rect.right() - margin
        
        # Y轴限制
        min_y = container_rect.top() - img_size.height() + margin
        max_y = container_rect.bottom() - margin

        # 如果图片比容器小，限制它不完全跑出中心区域
        new_x = max(min_x, min(pos.x(), max_x))
        new_y = max(min_y, min(pos.y(), max_y))
        
        return QPoint(new_x, new_y)

    def apply_zoom(self, factor):
        """执行缩放并保持中心点不变"""
        if not self.pix_raw: return
        
        old_size = self.image_label.size()
        old_pos = self.image_label.pos()
        
        # 计算新尺寸
        new_size = self.size * factor
        if new_size.width() > 5000:
            self.btn_sleep('btn_big')
            return
        if new_size.width() < 100:
            self.btn_sleep('btn_small')
            return
            
        self.size = new_size
        self.pix = self.pix_raw.scaled(self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(self.pix)
        self.image_label.resize(self.pix.size())

        # 计算位置偏移：保持图片中心点位置不变
        # Offset = (OldSize - NewSize) / 2
        diff_w = (old_size.width() - self.image_label.width()) // 2
        diff_h = (old_size.height() - self.image_label.height()) // 2
        
        new_pos = QPoint(old_pos.x() + diff_w, old_pos.y() + diff_h)
        self.image_label.move(self._limit_image_position(new_pos))

    def image_biger(self):
        self.apply_zoom(1.2)
        self.btn_wakeUp('btn_small')

    def image_smaller(self):
        self.apply_zoom(0.8)
        self.btn_wakeUp('btn_big')

    def show_image(self):
        if self.file_num == 0:
            self.pix_raw = None
            self.getWidget('image').setPixmap(QPixmap(assetsUrl('image', 'error.png')))
            return

        current_file = self.files[self.current]
        raw_path = os.path.join(self.savePath, current_file)
        
        self.setWindowTitle(current_file)

        self.pix_raw = QPixmap(raw_path)
        self.size = QSize(960, 672) # 重置基准尺寸
        self.pix = self.pix_raw.scaled(self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(self.pix)
        self.image_label.resize(self.pix.size())
        
        QTimer.singleShot(30, self._reset_image_position)

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

    def left_image(self):
        if self.current > 0:
            self.current -= 1
            self.show_image()
            self.update_navigation_buttons()

    def right_image(self):
        if self.current < self.file_num - 1:
            self.current += 1
            self.show_image()
            self.update_navigation_buttons()

    def refresh_file_list(self):
        if not os.path.isdir(self.savePath):
            self.files = []; self.file_num = 0
            return
        self.files = sorted([f for f in os.listdir(self.savePath) if os.path.splitext(f)[1].lower() in self.supported_extensions])
        self.file_num = len(self.files)

    def locate_current_image(self):
        target = os.path.basename(self.currentPath)
        self.current = self.files.index(target) if target in self.files else 0

    def update_navigation_buttons(self):
        if self.file_num <= 1:
            self.btn_sleep('btn_left'); 
            self.btn_sleep('btn_right')
        elif self.current == 0:
            self.btn_sleep('btn_left'); 
            self.btn_wakeUp('btn_right')
        elif self.current == self.file_num - 1:
            self.btn_sleep('btn_right'); 
            self.btn_wakeUp('btn_left')
        else:
            self.btn_wakeUp('btn_left'); 
            self.btn_wakeUp('btn_right')

    def btn_sleep(self, name):
        self.setClass(name, f'{name}_sleep')

    def btn_wakeUp(self, name):
        self.setClass(name, name)
    
    def close_page(self):
        self.close()
        self.image_request.emit(None)
        self.widgetsController.destroy()
        self.deleteLater()