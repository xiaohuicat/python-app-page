import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode('utf-8')


def base64_to_image(base64_string, image_path):
    with open(image_path, "wb") as image_file:
        decoded_string = base64.b64decode(base64_string)
        image_file.write(decoded_string)


def png_to_ico(png_path, ico_path):
    from PIL import Image
    # 加载PNG图片
    img = Image.open(png_path)

    # 保存为ICO格式
    img.save(ico_path, format="ICO")