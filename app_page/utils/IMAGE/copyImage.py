from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QImageReader

def copy_image_to_clipboard(image_path):
    # 获取图像数据
    image_reader = QImageReader(image_path)
    image_data = image_reader.read()

    # 将图像数据复制到剪贴板
    clipboard = QApplication.clipboard()
    clipboard.setPixmap(QPixmap.fromImage(image_data))

