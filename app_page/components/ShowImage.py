import os
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QPixmap, QGuiApplication
from ..assets.UI.ui_image import Ui_MainWindow as Ui_Image
from ..core import Page
from ..core.Device import getScreenInfo
from ..animation import MoveWin, Shadow

from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


class ShowImage(QMainWindow):
    image_request = Signal(object)

    def __init__(self, page: Page, savePath: str, currentPath: str):
        super().__init__()
        self.param = page.param

        MoveWin(self, page.param, "image_window_position")

        self.ui = Ui_Image()
        self.ui.setupUi(self)

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        Shadow(self.ui.frame_main)

        # 按钮连接
        self.ui.btn_change.clicked.connect(self.restore_or_maximize_window)
        self.ui.btn_mini.clicked.connect(self.showMinimized)
        self.ui.btn_big.clicked.connect(self.image_biger)
        self.ui.btn_small.clicked.connect(self.image_smaller)
        self.ui.btn_left.clicked.connect(self.left_image)
        self.ui.btn_right.clicked.connect(self.right_image)
        self.ui.btn_close.clicked.connect(self.close)

        # 路径处理
        self.savePath = savePath.rstrip('/\\')
        self.currentPath = currentPath

        # 显示参数
        self.size = QSize(960, 672)
        self.isMaximized = False
        self.normal_window_rect = None

        self.screen = getScreenInfo()

        # 支持的图片格式
        self.supported_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff', '.svg'}

        # 初始化文件列表并定位当前图片
        self.refresh_file_list()
        self.locate_current_image()

        # 显示图片并更新导航按钮
        self.show_image()
        self.update_navigation_buttons()

    def refresh_file_list(self):
        """刷新文件夹中的图片文件列表（按文件名排序）"""
        if not os.path.isdir(self.savePath):
            self.files = []
            self.file_num = 0
            return

        all_files = os.listdir(self.savePath)
        self.files = sorted([
            f for f in all_files
            if os.path.splitext(f)[1].lower() in self.supported_extensions
            and os.path.isfile(os.path.join(self.savePath, f))
        ])
        self.file_num = len(self.files)

    def locate_current_image(self):
        """根据 currentPath 定位到对应的图片索引"""
        if self.file_num == 0:
            self.current = 0
            return

        target_filename = os.path.basename(self.currentPath)

        if target_filename in self.files:
            self.current = self.files.index(target_filename)
        else:
            # 如果指定图片不在文件夹中（可能被删除或路径错误），默认显示第一张
            self.current = 0

    def update_navigation_buttons(self):
        """根据当前图片位置更新左右按钮的可用状态"""
        if self.file_num <= 1:
            self.btn_sleep('btn_left')
            self.btn_sleep('btn_right')
            return

        if self.current == 0:
            self.btn_sleep('btn_left')
            self.btn_wakeUp('btn_right')
        elif self.current == self.file_num - 1:
            self.btn_sleep('btn_right')
            self.btn_wakeUp('btn_left')
        else:
            self.btn_wakeUp('btn_left')
            self.btn_wakeUp('btn_right')

        # 缩放按钮初始状态（假设图片可放大）
        self.btn_wakeUp('btn_big')
        self.btn_sleep('btn_small')  # 初始不允许缩小（因为还没放大）

    def show_image(self):
        """显示当前索引的图片"""
        if self.file_num == 0:
            self.pix_raw = False
            error_pix = QPixmap(os.path.join(os.getcwd(), 'assets/image/error.png'))
            self.ui.label.setPixmap(error_pix)
            self.setWindowTitle("无图片")
            return

        current_file = self.files[self.current]
        raw_path = os.path.join(self.savePath, current_file)

        print('正在查看:', raw_path)

        # 更新窗口标题为当前图片文件名
        self.setWindowTitle(current_file)

        # 生成缩略图路径（800x800）
        name_no_ext = os.path.splitext(current_file)[0]
        thumbnail_name = name_no_ext + '.png'
        thumbnail_dir = self.param.pathJoin(
            "tempPath", 'images/show/thumbnail_size_800',
            os.path.basename(self.savePath)
        )
        new_path_800 = os.path.join(thumbnail_dir, thumbnail_name)

        isError = False
        if os.path.isfile(new_path_800):
            print('缩略图已存在:', new_path_800)
        else:
            os.makedirs(thumbnail_dir, exist_ok=True)
            try:
                with Image.open(raw_path) as img:
                    img.thumbnail((800, 800))
                    img.save(new_path_800)
            except Exception as e:
                print("无法打开或处理图片:", raw_path, e)
                isError = True

        if isError:
            self.pix_raw = False
            self.pix = QPixmap(os.path.join(os.getcwd(), 'assets/image/error.png'))
        else:
            self.pix_raw = QPixmap(new_path_800)
            if self.pix_raw.isNull():
                self.pix_raw = False
                self.pix = QPixmap(os.path.join(os.getcwd(), 'assets/image/error.png'))
            else:
                self.pix = self.pix_raw.scaled(
                    self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )

        self.ui.label.setPixmap(self.pix)

    # 上一张
    def left_image(self):
        if self.current > 0:
            self.current -= 1
            self.refresh_file_list()  # 防止文件被外部删除
            if self.current >= self.file_num:
                self.current = self.file_num - 1
            self.show_image()
            self.update_navigation_buttons()

    # 下一张
    def right_image(self):
        if self.current < self.file_num - 1:
            self.current += 1
            self.refresh_file_list()
            if self.current >= self.file_num:
                self.current = 0
            self.show_image()
            self.update_navigation_buttons()

    # 放大
    def image_biger(self):
        if not self.pix_raw or self.pix_raw.isNull():
            print('没有加载有效原图')
            return

        current_w, current_h = self.size.width(), self.size.height()
        if current_w >= 6000 or current_h >= 6000:
            print('已达到最大放大')
            self.btn_sleep('btn_big')
            return

        self.size = self.size * 1.2
        self.pix = self.pix_raw.scaled(self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.label.setPixmap(self.pix)

        self.btn_wakeUp('btn_big')
        if current_w > 100 and current_h > 100:
            self.btn_wakeUp('btn_small')

    # 缩小
    def image_smaller(self):
        if not self.pix_raw or self.pix_raw.isNull():
            print('没有加载有效原图')
            return

        current_w, current_h = self.size.width(), self.size.height()
        if current_w <= 100 or current_h <= 100:
            print('已达到最小尺寸')
            self.btn_sleep('btn_small')
            return

        self.size = self.size * 0.8
        self.pix = self.pix_raw.scaled(self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.label.setPixmap(self.pix)

        self.btn_wakeUp('btn_small')
        if current_w < 6000 and current_h < 6000:
            self.btn_wakeUp('btn_big')

    # 最大化 / 还原
    def restore_or_maximize_window(self):
        if self.isMaximized:
            if self.normal_window_rect:
                self.setGeometry(*self.normal_window_rect)
            self.isMaximized = False
            self.ui.btn_change.setStyleSheet(
                'image:url(./assets/icon/image/btn_change.png);padding:6px;'
            )
        else:
            raw = self.geometry()
            self.normal_window_rect = [raw.x(), raw.y(), raw.width(), raw.height()]
            rect = QGuiApplication.primaryScreen().availableGeometry()
            self.setGeometry(-8, -8, rect.width() + 16, rect.height() + 40)
            self.isMaximized = True
            self.ui.btn_change.setStyleSheet(
                'image:url(./assets/icon/image/btn_change_sleep.png);padding:4px;'
            )

    # 按钮禁用样式
    def btn_sleep(self, name):
        btn = getattr(self.ui, name)
        btn.setStyleSheet(
            f'#{name}{{image:url(./assets/icon/image/{name}_sleep.png)}}'
            f'#{name}:hover{{background-color:#fff;}}'
        )

    # 按钮启用样式
    def btn_wakeUp(self, name):
        btn = getattr(self.ui, name)
        btn.setStyleSheet(
            f'#{name}{{image:url(./assets/icon/image/{name}.png)}}'
        )