import os, ctypes

def set_img_as_wallpaper(filepath):
  filepath = os.path.abspath(filepath)
  ctypes.windll.user32.SystemParametersInfoW(20, 0, filepath, 0)

set_img_as_wallpaper('wallhaven-7pmply.jpg')