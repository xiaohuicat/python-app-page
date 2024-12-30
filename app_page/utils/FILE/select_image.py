import time, os
from PySide6.QtWidgets import QFileDialog
from utils.IMAGE.cut_image import cut_image_out

def select_image(target, dist, title="选择背景图片", size=(1920, 1080)):
  imgName, imgType = QFileDialog.getOpenFileName(target, title, "", "*.jpg;;*.png;;All Files(*)")
  if not os.path.exists(dist):
    os.mkdir(dist)
  output = f'{dist}/{int(time.time()*1000)}.{imgName.split(".")[-1]}'
  abs_output = os.path.abspath(output)
  cut_image_out(imgName, abs_output, size)
  return output, abs_output