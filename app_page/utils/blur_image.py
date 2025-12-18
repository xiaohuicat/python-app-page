import os
from PIL import Image, ImageFilter
from .file_handle import get_file_md5, create_folder


def blur_image(save_folder: str, image_path: str, blur_radius: float = 5.0, opacity: float = 1.0) -> str:
    """
    读取图片进行模糊处理，设置透明度并转为PNG格式，缓存处理结果避免重复计算，返回模糊图片保存路径
    
    Args:
        save_folder: 处理后图片的保存文件夹
        image_path: 原始图片的路径（必填）
        blur_radius: 模糊半径（选填，默认5.0，值越大模糊效果越强）
        opacity: 透明度（选填，默认1.0，范围0.0-1.0，0为完全透明，1为完全不透明）
    
    Returns:
        模糊处理后的PNG图片保存路径
    
    Raises:
        FileNotFoundError: 原始图片路径不存在
        ValueError: 模糊半径为负数 / 透明度超出0-1范围
        IOError: 图片文件损坏或格式不支持
    """
    # 1. 参数校验
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"原始图片不存在: {image_path}")
    
    if blur_radius < 0:
        raise ValueError(f"模糊半径不能为负数，当前值: {blur_radius}")
    
    if not (0.0 <= opacity <= 1.0):
        raise ValueError(f"透明度必须在0.0-1.0之间，当前值: {opacity}")
    
    # 2. 计算原始图片的MD5（用于唯一标识原图）
    original_md5 = get_file_md5(image_path)
    
    # 3. 构建模糊图片的保存路径（强制PNG格式，文件名包含MD5、模糊半径、透明度）
    create_folder(save_folder)  # 保存文件夹不存在则创建
    blur_img_name = f"{original_md5}_blur{blur_radius}_opacity{opacity}.png"  # 强制PNG后缀
    blur_img_path = os.path.join(save_folder, blur_img_name).replace("\\", "/")
    
    # 4. 缓存检查：如果已存在相同参数的模糊图片，直接返回路径
    if os.path.exists(blur_img_path):
        return blur_img_path
    
    try:
        with Image.open(image_path) as img:
            # 统一转为RGB格式（避免不同模式干扰透明度处理）
            rgb_img = img.convert('RGB')
            
            # 执行高斯模糊
            blurred_rgb = rgb_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            
            # 添加透明度通道并设置指定透明度
            # 先转为RGBA模式（R/G/B/Alpha），Alpha通道值范围0-255
            alpha_value = int(opacity * 255)
            # 创建全为alpha_value的透明度通道
            alpha_channel = Image.new('L', blurred_rgb.size, alpha_value)
            # 合并RGB和透明度通道，得到RGBA图片
            blurred_img = Image.merge('RGBA', (*blurred_rgb.split(), alpha_channel))
            
            # 强制保存为PNG格式（支持透明度）
            blurred_img.save(blur_img_path, format='PNG')
            
    except Exception as e:
        raise IOError(f"图片处理失败: {str(e)}") from e
    
    return blur_img_path