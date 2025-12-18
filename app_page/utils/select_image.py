import time
import os
from typing import Tuple, Optional
from PySide6.QtWidgets import QFileDialog
from .cut_image import cut_image_out


def select_image(
    target, 
    dist: str, 
    title: str = "选择背景图片", 
    size: Tuple[int, int] = (1920, 1080)
) -> Tuple[Optional[str], Optional[str]]:
    """
    选择图片并裁剪到指定尺寸。
    
    Args:
        target: 父窗口对象
        dist: 输出目录路径
        title: 文件选择对话框标题
        size: 裁剪后的图片尺寸，默认为(1920, 1080)
        
    Returns:
        Tuple[Optional[str], Optional[str]]: 返回(相对路径, 绝对路径)的元组，如果用户取消则返回(None, None)
    """
    # 选择图片文件
    imgName, imgType = QFileDialog.getOpenFileName(
        target, 
        title, 
        "", 
        "图片文件 (*.jpg *.jpeg *.png *.bmp);;所有文件 (*.*)"
    )
    
    # 用户取消选择
    if not imgName:
        return None, None
    
    try:
        # 确保输出目录存在
        os.makedirs(dist, exist_ok=True)
        
        # 生成输出文件名
        file_ext = os.path.splitext(imgName)[1].lower()
        timestamp = int(time.time() * 1000)
        output = os.path.join(dist, f"{timestamp}{file_ext}")
        abs_output = os.path.abspath(output)
        
        # 裁剪图片
        cut_image_out(imgName, abs_output, size)
        
        return output, abs_output
    
    except Exception as e:
        print(f"处理图片时出错: {e}")
        return None, None