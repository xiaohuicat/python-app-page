import os
from PySide6.QtCore import Signal, Qt, QSize, QPoint, QEvent, QTimer
from PySide6.QtWidgets import QMainWindow, QWidget, QLayout, QLabel, QHBoxLayout, QGridLayout
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
            <div>
                <h-box spacing="0" margins="[0,0,0,0]">
                    <div id="image_container">
                        <h-box id="image_layout" align="AlignCenter" margins="[0,0,0,0]" spacing="0">
                            <label id="image" />
                        </h-box>
                    </div>
                    <div id="right_panel" width="0" class="side_panel">
                        <grid id="list_grid" grid="[0, 3]" spacing="8" margins="[10,10,10,10]" align="AlignTop"/>
                    </div>
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
    image_request = Signal(object)

    def __init__(self, currentPath:str|None = None, images:list|None = None):
        super().__init__()
        self.images = images if images else []
        self.image_num = len(self.images)
        self.currentPath = currentPath if currentPath else ''
        self.current = self.images.index(self.currentPath) if self.currentPath in self.images else 0

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
            widget_list=render_dict['widget_list']
        )
        
        # 基础控件
        self.image_label: QLabel = self.getWidget('image')
        self.image_container: QWidget = self.getWidget('image_container')
        self.image_layout: QHBoxLayout = self.getWidget('image_layout')
        
        # 列表控件
        self.right_panel: QWidget = self.getWidget('right_panel')
        self.list_grid: QGridLayout = self.getWidget('list_grid')
        self.is_list_show = False

        # 信号绑定
        self.register('btn_change', 'clicked', self.restore_or_maximize_window)
        self.register('btn_mini', 'clicked', self.showMinimized)
        self.register('btn_big', 'clicked', self.image_biger)
        self.register('btn_small', 'clicked', self.image_smaller)
        self.register('btn_left', 'clicked', self.left_image)
        self.register('btn_right', 'clicked', self.right_image)
        self.register('btn_close', 'clicked', self.close_page)
        self.register('btn_list', 'clicked', self.toggle_list)

        self.size = QSize(960, 672)
        self.isMaximized = False
        self.normal_window_rect = None
        self.supported_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff', '.svg'}

        self.is_dragging = False
        self.drag_start_offset = QPoint() 

        self.image_layout.removeWidget(self.image_label)
        self.image_label.setParent(self.image_container)
        self.image_label.setMouseTracking(True)
        self.image_label.installEventFilter(self)

        if self.has_image():
            self.show_image()

    def register(self, id:str, signal:str, callback):
        self.widgetsController.register(id, signal, callback)

    def setClass(self, id:str, className:str):
        self.widgetsController.setClass(id, className)

    def getWidget(self, id:str) -> QWidget|QLayout:
        return self.widgetsController.getWidget(id)

    # --- 列表功能实现 ---
    def toggle_list(self):
        """展开或收起侧边列表"""
        if self.is_list_show:
            self.right_panel.setFixedWidth(0)
            self.is_list_show = False
        else:
            self.right_panel.setFixedWidth(240)
            self.is_list_show = True
            if self.list_grid.count() == 0:
                self.refresh_thumb_list()
            else:
                self._update_list_highlight()
        
        # 布局改变后重新计算主图位置
        QTimer.singleShot(50, self._reset_image_position)

    def refresh_thumb_list(self):
        """生成64x64缩略图列表"""
        # 清空旧列表
        while self.list_grid.count():
            item = self.list_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for index, path in enumerate(self.images):
            thumb = QLabel()
            thumb.setFixedSize(64, 64)
            thumb.setScaledContents(True)
            thumb.setProperty("path_index", index)
            thumb.setCursor(Qt.PointingHandCursor)
            
            # 缩略图加载
            pix = QPixmap(path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            thumb.setPixmap(pix)
            thumb.installEventFilter(self)
            
            row, col = divmod(index, 3)
            self.list_grid.addWidget(thumb, row, col)
            
        self._update_list_highlight()

    def _update_list_highlight(self):
        """更新列表中的选中状态样式"""
        if not self.is_list_show: return
        for i in range(self.list_grid.count()):
            widget = self.list_grid.itemAt(i).widget()
            if widget:
                if widget.property("path_index") == self.current:
                    widget.setStyleSheet("border: 2px solid #0078d7; border-radius:0px; background: rgba(0,120,215,0.1);")
                else:
                    widget.setStyleSheet("border: 2px solid transparent;")

    # --- 核心逻辑 ---
    def eventFilter(self, obj, event):
        # 拦截缩略图点击
        if isinstance(obj, QLabel) and obj.property("path_index") is not None:
            if event.type() == QEvent.MouseButtonPress:
                self.current = obj.property("path_index")
                self.show_image()
                return True

        # 主图交互逻辑
        if obj == self.image_label:
            if not hasattr(self, 'pix_raw') or not self.pix_raw:
                return super().eventFilter(obj, event)

            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.is_dragging = True
                self.drag_start_offset = event.pos()
                self.image_label.setCursor(Qt.ClosedHandCursor)
                return True

            elif event.type() == QEvent.MouseMove and self.is_dragging:
                container_pos = self.image_container.mapFromGlobal(event.globalPos())
                new_pos = container_pos - self.drag_start_offset
                self.image_label.move(self._limit_image_position(new_pos))
                return True

            elif event.type() == QEvent.MouseButtonRelease:
                self.is_dragging = False
                self.image_label.setCursor(Qt.OpenHandCursor)
                return True

            elif event.type() == QEvent.Enter:
                self.image_label.setCursor(Qt.OpenHandCursor)
            
            elif event.type() == QEvent.Wheel:
                self.image_biger() if event.angleDelta().y() > 0 else self.image_smaller()
                return True

        return super().eventFilter(obj, event)

    def _reset_image_position(self):
        if not self.image_label.pixmap(): return
        container_rect = self.image_container.contentsRect()
        pix_size = self.image_label.pixmap().size()
        center_x = (container_rect.width() - pix_size.width()) // 2
        center_y = (container_rect.height() - pix_size.height()) // 2
        self.image_label.resize(pix_size)
        self.image_label.move(center_x, center_y)

    def _limit_image_position(self, pos: QPoint) -> QPoint:
        container_rect = self.image_container.contentsRect()
        img_size = self.image_label.size()
        margin = 20 
        min_x, max_x = container_rect.left() - img_size.width() + margin, container_rect.right() - margin
        min_y, max_y = container_rect.top() - img_size.height() + margin, container_rect.bottom() - margin
        return QPoint(max(min_x, min(pos.x(), max_x)), max(min_y, min(pos.y(), max_y)))

    def apply_zoom(self, factor):
        if not hasattr(self, 'pix_raw') or self.pix_raw.isNull(): return
        old_size, old_pos = self.image_label.size(), self.image_label.pos()
        new_size = self.size * factor
        if new_size.width() > 5000 or new_size.width() < 100: return
        
        self.size = new_size
        self.pix = self.pix_raw.scaled(self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(self.pix)
        self.image_label.setFixedSize(self.pix.size())
        
        diff_w = (old_size.width() - self.image_label.width()) // 2
        diff_h = (old_size.height() - self.image_label.height()) // 2
        self.image_label.move(self._limit_image_position(QPoint(old_pos.x() + diff_w, old_pos.y() + diff_h)))

    def image_biger(self):
        self.apply_zoom(1.2)
    def image_smaller(self):
        self.apply_zoom(0.8)
    def has_image(self):
        return self.image_num > 0

    def show_image(self):
        if self.image_num == 0:
            return
        raw_path = self.images[self.current]
        self.setWindowTitle(os.path.basename(raw_path))
        self.pix_raw = QPixmap(raw_path)
        self.size = QSize(960, 672)
        self.pix = self.pix_raw.scaled(self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(self.pix)
        self.image_label.setFixedSize(self.pix.size())
        
        QTimer.singleShot(30, self._reset_image_position)
        self.update_navigation_buttons()
        self._update_list_highlight()
        self.show()

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

    def right_image(self):
        if self.current < self.image_num - 1:
            self.current += 1
            self.show_image()

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

    def btn_sleep(self, name):
        self.setClass(name, f'{name}_sleep')
    def btn_wakeUp(self, name):
        self.setClass(name, name)
    
    def close_page(self):
        self.close()
        self.image_request.emit(None)
        self.widgetsController.destroy()
        self.deleteLater()