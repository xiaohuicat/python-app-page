import base64
import os
from typing import Optional, Tuple, Union

from PIL import Image
from PIL import ImageFile
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QImageReader, QImage


# 设置PIL加载截断图片的全局配置
ImageFile.LOAD_TRUNCATED_IMAGES = True


def image_to_base64(image_path: str) -> Optional[str]:
    """
    将图片文件转换为Base64编码字符串
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        Base64编码字符串，如果出错返回None
    """
    # 前置检查：文件是否存在
    if not os.path.exists(image_path):
        print(f"错误：文件 {image_path} 不存在")
        return None
    
    try:
        with open(image_path, "rb") as image_file:
            encoded_bytes = base64.b64encode(image_file.read())
            return encoded_bytes.decode('utf-8')
    except Exception as e:
        print(f"转换Base64失败：{str(e)}")
        return None


def base64_to_image(base64_string: str, image_path: str) -> bool:
    """
    将Base64编码字符串转换为图片文件
    
    Args:
        base64_string: Base64编码字符串
        image_path: 保存图片的路径
        
    Returns:
        成功返回True，失败返回False
    """
    # 前置检查：确保目录存在
    output_dir = os.path.dirname(image_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 处理可能的URL安全Base64编码
        base64_string = base64_string.replace('-', '+').replace('_', '/')
        decoded_bytes = base64.b64decode(base64_string)
        
        with open(image_path, "wb") as image_file:
            image_file.write(decoded_bytes)
        return True
    except base64.binascii.Error as e:
        print(f"Base64解码失败：{str(e)}")
        return False
    except Exception as e:
        print(f"保存图片失败：{str(e)}")
        return False


def png_to_ico(png_path: str, ico_path: str, sizes: Tuple[int, ...] = (16, 32, 48, 64, 128, 256)) -> bool:
    """
    将PNG图片转换为ICO图标文件（支持多尺寸）
    
    Args:
        png_path: PNG文件路径
        ico_path: ICO保存路径
        sizes: ICO包含的尺寸列表
        
    Returns:
        成功返回True，失败返回False
    """
    if not os.path.exists(png_path):
        print(f"错误：PNG文件 {png_path} 不存在")
        return None
    
    try:
        with Image.open(png_path) as img:
            # 确保图片是RGBA格式（ICO推荐格式）
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 生成多尺寸ICO
            img_sizes = [(size, size) for size in sizes if size <= max(img.size)]
            img.save(ico_path, format="ICO", sizes=img_sizes)
        return True
    except Exception as e:
        print(f"转换ICO失败：{str(e)}")
        return False


def img_to_png(raw_file_path: str, new_file_path: str, max_size: Tuple[int, int] = (256, 256)) -> bool:
    """
    将任意格式图片转换为PNG格式，并按最大尺寸等比例缩放
    
    Args:
        raw_file_path: 原始图片路径
        new_file_path: 新PNG文件保存路径
        max_size: 最大尺寸(宽, 高)
        
    Returns:
        成功返回True，失败返回False
    """
    if not os.path.exists(raw_file_path):
        print(f"错误：原始文件 {raw_file_path} 不存在")
        return False
    
    try:
        with Image.open(raw_file_path) as img:
            original_width, original_height = img.size
            
            # 计算等比例缩放后的尺寸（修复原代码逻辑错误）
            if original_width > max_size[0] or original_height > max_size[1]:
                # 计算缩放比例（取最小比例保证不超出限制）
                width_ratio = max_size[0] / original_width
                height_ratio = max_size[1] / original_height
                scale_ratio = min(width_ratio, height_ratio)
                
                new_width = int(original_width * scale_ratio)
                new_height = int(original_height * scale_ratio)
            else:
                new_width, new_height = original_width, original_height
            
            # 只有尺寸变化时才缩放
            if (new_width, new_height) != (original_width, original_height):
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 确保输出目录存在
            output_dir = os.path.dirname(new_file_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # 保存为PNG格式（确保RGB/A格式）
            if img.mode in ('P', 'RGBA'):
                img = img.convert('RGBA')
            else:
                img = img.convert('RGB')
            
            img.save(new_file_path, format='PNG', optimize=True)
        return True
    except Exception as e:
        print(f"转换PNG失败：{str(e)}")
        return False


def copy_image(image_path: str) -> bool:
    """
    将图片复制到系统剪贴板
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        成功返回True，失败返回False
    """
    if not os.path.exists(image_path):
        print(f"错误：图片文件 {image_path} 不存在")
        return False
    
    try:
        # 初始化QApplication（如果尚未初始化）
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 读取图片
        image_reader = QImageReader(image_path)
        image: Optional[QImage] = image_reader.read()
        
        if image.isNull():
            print(f"错误：无法读取图片 {image_path}")
            return False
        
        # 复制到剪贴板
        clipboard = app.clipboard()
        clipboard.setPixmap(QPixmap.fromImage(image))
        return True
    except Exception as e:
        print(f"复制到剪贴板失败：{str(e)}")
        return False