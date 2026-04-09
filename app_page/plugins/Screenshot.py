import os
import time
import logging
from typing import Optional, Callable

from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPen, QPainter, QColor, QGuiApplication, QFont, QMouseEvent, QKeyEvent
from PySide6.QtWidgets import QWidget

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Screenshot(QWidget):
    """高质量截图工具（优化版）"""

    def __init__(self, save_folder: str, callback: Optional[Callable[[str], None]] = None):
        super().__init__()
        # 实例变量（修复原代码类变量共享问题）
        self.fullScreenImage = None
        self.captureImage = None
        self.isMousePressLeft = False
        self.beginPosition: Optional[QPoint] = None
        self.endPosition: Optional[QPoint] = None

        # 回调与保存路径
        self.callback = callback
        self.savePath = os.path.abspath(os.path.join(save_folder, "screenshot"))

        # 初始化
        self.initWindow()
        self.captureFullScreen()
        self.show()

    def initWindow(self) -> None:
        """初始化窗口：无边框、全屏、十字光标"""
        self.setCursor(Qt.CrossCursor)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # 置顶更友好
        self.setAttribute(Qt.WA_TranslucentBackground)  # 半透明背景更流畅
        self.setWindowState(Qt.WindowFullScreen)
        self.setMinimumSize(100, 100)  # 防止异常缩成0大小

    def captureFullScreen(self) -> None:
        """捕获全屏图像（自动适配多显示器 + DPI）"""
        screen = QGuiApplication.primaryScreen()
        if not screen:
            screen = QGuiApplication.screens()[0]
        self.fullScreenImage = screen.grabWindow(0)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """鼠标左键开始截图，右键取消/退出"""
        if event.button() == Qt.LeftButton:
            self.beginPosition = event.pos()
            self.isMousePressLeft = True
            self.captureImage = None

        elif event.button() == Qt.RightButton:
            if self.captureImage is not None:
                self.captureImage = None
                self.update()
            else:
                self.close()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """鼠标拖动实时更新选区"""
        if self.isMousePressLeft and self.beginPosition:
            self.endPosition = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """鼠标松开完成选区绘制"""
        self.isMousePressLeft = False
        self.update()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """双击确认保存"""
        if event.button() == Qt.LeftButton:
            self.saveAndExit()

    def getValidRect(self, start: QPoint, end: QPoint) -> QRect:
        """获取合法矩形：自动处理方向 + 最小尺寸"""
        rect = QRect(start, end).normalized()
        # 最小 10x10，防止无效截图
        if rect.width() < 10 or rect.height() < 10:
            return QRect()
        return rect

    def paintEvent(self, event) -> None:
        """绘制事件（painter 必须局部创建！）"""
        if not self.fullScreenImage:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿更清晰

        # 1. 绘制全屏背景 + 半透明遮罩
        painter.drawPixmap(0, 0, self.fullScreenImage)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        # 2. 没有选区直接结束
        if not self.beginPosition or not self.endPosition:
            return

        # 3. 获取缩放比例（解决高分屏模糊/偏移）
        scale = self.devicePixelRatio()
        select_rect = self.getValidRect(self.beginPosition, self.endPosition)
        if select_rect.isEmpty():
            return

        # 4. 绘制截图区域（清晰显示）
        capture_rect = select_rect * scale
        self.captureImage = self.fullScreenImage.copy(capture_rect)
        painter.drawPixmap(select_rect, self.captureImage)

        # 5. 绘制蓝色边框
        painter.setPen(QPen(QColor(30, 150, 255), 2, Qt.SolidLine))
        painter.drawRect(select_rect)

        # 6. 绘制尺寸文字
        self.drawInfoText(painter, select_rect)

    def drawInfoText(self, painter: QPainter, rect: QRect) -> None:
        """绘制尺寸提示 + 操作提示"""
        font = QFont("Segoe UI", 10, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#ffffff"))

        # 尺寸文字
        w, h = rect.width(), rect.height()
        text = f"{w} × {h}"
        x = rect.x() + 5
        y = rect.y() - 8 if rect.y() > 20 else rect.y() + 15
        painter.drawText(x, y, text)

        # 操作提示
        tip = "Enter 确认 | Esc 退出 | 右键 取消"
        tip_x = rect.right() - 160
        tip_y = rect.bottom() + 16
        if tip_x < 10:
            tip_x = 10
        painter.drawText(tip_x, tip_y, tip)

    def saveImage(self) -> Optional[str]:
        """保存截图到文件（带异常处理）"""
        try:
            if not os.path.exists(self.savePath):
                os.makedirs(self.savePath, exist_ok=True)

            file_name = time.strftime("%Y%m%d-%H%M%S") + ".png"
            file_path = os.path.join(self.savePath, file_name)

            if self.captureImage and not self.captureImage.isNull():
                self.captureImage.save(file_path, "PNG")
            else:
                self.fullScreenImage.save(file_path, "PNG")

            logging.info(f"截图已保存：{file_path}")
            return file_path

        except Exception as e:
            logging.error(f"保存失败：{str(e)}")
            return None

    def saveAndExit(self) -> None:
        """保存并关闭窗口"""
        path = self.saveImage()
        if path and self.callback:
            self.callback(path)
        self.close()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """键盘快捷键"""
        key = event.key()
        if key == Qt.Key_Escape:
            self.close()
        elif key in (Qt.Key_Enter, Qt.Key_Return):
            self.saveAndExit()