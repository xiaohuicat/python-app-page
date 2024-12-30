from PIL import Image

def cut_image_in(input_path, output_path=None, target_size_WH=(256, 256)):
    # 打开图片
    image = Image.open(input_path)

    # 获取图片的宽度和高度
    width, height = image.size
    if width < height:
        # 高度是长边，宽度按比例缩放
        new_height = target_size_WH[1]
        new_width = int((target_size_WH[1] / height)*width)
    else:
        # 宽度是长边，高度按比例缩放
        new_width = target_size_WH[0]
        new_height = int((target_size_WH[0] / width)*height)

    cropped_image = image.resize((new_width, new_height), Image.LANCZOS)

    # print([width,height],[new_width, new_height])

    # 创建一个空白的256x256的画布
    final_image = Image.new("RGB", (target_size_WH[0], target_size_WH[1]), (255, 255, 255))
    # 将裁剪后的图片粘贴到画布中间
    final_image.paste(cropped_image, ((target_size_WH[0] - new_width) // 2, (target_size_WH[1] - new_height) // 2))

    # 保存裁剪后的图片
    if output_path:
        final_image.save(output_path)

    # print(final_image.size)

    return final_image

def cut_image_out(input_path, output_path=None, target_size_WH=(256, 256)):
    # 打开图片
    image = Image.open(input_path)

    # 获取图片的宽度和高度
    width, height = image.size
    if width < height:
        # 高度是长边，宽度按比例缩放
        new_width = target_size_WH[0]
        new_height = int((target_size_WH[0] / width)*height)
    else:
        # 宽度是长边，高度按比例缩放
        new_height = target_size_WH[1]
        new_width = int((target_size_WH[1] / height)*width)

    cropped_image = image.resize((new_width, new_height), Image.LANCZOS)

    print([width,height],[new_width, new_height])

    # 创建一个空白的256x256的画布
    final_image = Image.new("RGB", (target_size_WH[0], target_size_WH[1]), (255, 255, 255))
    # 将裁剪后的图片粘贴到画布中间
    final_image.paste(cropped_image, ((target_size_WH[0] - new_width) // 2, (target_size_WH[1] - new_height) // 2))

    # 保存裁剪后的图片
    if output_path:
      final_image.save(output_path)
    
    # print(final_image.size)

    return final_image