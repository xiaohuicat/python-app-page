from PIL import Image, ImageDraw, ImageOps

def add_rounded_corners(image_path, output_path, corner_radius):
    # 打开图片
    image = Image.open(image_path).convert("RGBA")

    # 创建一个与图片相同大小的透明背景
    mask = Image.new("L", image.size, 0)

    # 为遮罩创建一个绘图对象
    draw = ImageDraw.Draw(mask)

    # 绘制一个白色的圆角矩形
    draw.rounded_rectangle((0, 0, image.width, image.height), corner_radius, fill=255)

    # 将遮罩应用到图像上，以获得圆角效果
    image_with_rounded_corners = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    image_with_rounded_corners.putalpha(mask)

    # 保存结果图片
    image_with_rounded_corners.save(output_path)

# 使用示例：
# input_image = r"C:\Users\xiaohuicat\Pictures\Saved Pictures\玫瑰3.png"
# output_image = r"C:\Users\xiaohuicat\Pictures\Saved Pictures\玫瑰3_rounded.png"
# input_image = r"C:\Users\xiaohuicat\Pictures\Saved Pictures\ren.png"
# output_image = r"C:\Users\xiaohuicat\Pictures\Saved Pictures\ren_rounded.png"
# add_rounded_corners(input_image, output_image, corner_radius=50)