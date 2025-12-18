from PIL import Image
from typing import Tuple, Optional
import os


def cut_image(
    input_path: str, 
    output_path: Optional[str] = None, 
    target_size_WH: Tuple[int, int] = (256, 256),
    mode: str = "in"
) -> Image.Image:
    """
    将图片裁剪并调整大小，保持宽高比，并居中放置在目标尺寸的画布上。
    
    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径，如果为None则不保存
        target_size_WH: 目标尺寸，格式为(宽度, 高度)
        mode: 裁剪模式，'in'表示内裁剪（保持整个图片在目标尺寸内），
                'out'表示外裁剪（填充整个目标尺寸，可能裁剪部分图片）
    
    返回:
        处理后的PIL图像对象
    
    异常:
        FileNotFoundError: 输入文件不存在
        ValueError: 参数值无效
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")
    
    if mode not in ["in", "out"]:
        raise ValueError("模式必须是'in'或'out'")
    
    # 打开图片
    try:
        image = Image.open(input_path)
    except Exception as e:
        raise ValueError(f"无法打开图片: {e}")
    
    # 获取图片的宽度和高度
    width, height = image.size
    
    # 根据模式计算新的尺寸
    if mode == "in":
        if width < height:
            # 高度是长边，宽度按比例缩放
            new_height = target_size_WH[1]
            new_width = int((target_size_WH[1] / height) * width)
        else:
            # 宽度是长边，高度按比例缩放
            new_width = target_size_WH[0]
            new_height = int((target_size_WH[0] / width) * height)
    else:  # mode == "out"
        if width < height:
            # 高度是长边，宽度按比例缩放
            new_width = target_size_WH[0]
            new_height = int((target_size_WH[0] / width) * height)
        else:
            # 宽度是长边，高度按比例缩放
            new_height = target_size_WH[1]
            new_width = int((target_size_WH[1] / height) * width)
    
    # 调整图片大小
    cropped_image = image.resize((new_width, new_height), Image.LANCZOS)
    
    # 创建一个空白的画布
    final_image = Image.new("RGB", target_size_WH, (255, 255, 255))
    
    # 将裁剪后的图片粘贴到画布中间
    paste_position = (
        (target_size_WH[0] - new_width) // 2, 
        (target_size_WH[1] - new_height) // 2
    )
    final_image.paste(cropped_image, paste_position)
    
    # 保存裁剪后的图片
    if output_path:
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            final_image.save(output_path)
        except Exception as e:
            raise ValueError(f"保存图片失败: {e}")
    
    return final_image


# 为了向后兼容，保留原来的函数名
def cut_image_in(input_path, output_path=None, target_size_WH=(256, 256)):
    """
    内裁剪模式，保持整个图片在目标尺寸内。
    """
    return cut_image(input_path, output_path, target_size_WH, mode="in")


def cut_image_out(input_path, output_path=None, target_size_WH=(256, 256)):
    """
    外裁剪模式，填充整个目标尺寸，可能裁剪部分图片。
    """
    return cut_image(input_path, output_path, target_size_WH, mode="out")