from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

def toPNG(raw_filePath, new_filePath, size=(256,256)):
  try:
    img = Image.open(raw_filePath)
    size = (256, 256)
    img.thumbnail(size)
    img.save(new_filePath)
    return True
  except: 
    return False
