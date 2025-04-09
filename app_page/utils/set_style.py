import os
from PySide6.QtWidgets import QWidget
from app_page_core import Store
from .common import assetsPath

# 根据参数设置样式
def setAppStyle(target, default_theme):
  setting = target.param.child(target.param.pathJoin("userPath", "setting.json"), default_theme)
  id = setting.get("skinId", default_theme["skinId"])
  style = list(filter( lambda each: each['id'] == id, setting.get("skinStyle", default_theme['skinStyle'])))[0]
  image_path = style['app_bg_image'].replace('\\', '/') if type(style['app_bg_image']) is str else ''
  if not os.path.exists(image_path):
    image_path = assetsPath('skin', 'app_bg_image_1.png').replace('\\', '/')
  setWidgetStyleById(id='frame_header', style={"background-color": style['header_bg_color']}, cover=True)
  setWidgetStyleById(id='frame_main', style={
    "background-color": style['main_bg_color'],
    "border-image": f"url('{image_path}') stretch",
  }, cover=True)


def setWidgetStyleById(id:str, style:dict, cover:bool = False):
  store = Store()
  ui = store.get('ui', None)
  if not ui:
    raise Exception("ui not found")

  config = {"styleSheetList":[]}
  try:
    if not cover:
      config["styleSheetList"] = ui[id].styleSheet().split('\n')
  except:
    pass
  ret = f'#{id}'+'{'+ ";".join([key+":"+style[key] for key in style.keys()]) + '}'
  config["styleSheetList"].append(ret)
  styleText = '\n'.join(config["styleSheetList"])
  ui[id].setStyleSheet(styleText)


def setWidgetStyle(widget:QWidget, style:dict|list, id=None, cover:bool = False):
  if isinstance(style, list):
    style = cascading_styles(*style)
  
  config = {"styleSheetList":[]}
  try:
    if not cover:
      config["styleSheetList"] = widget.styleSheet().split('\n')
  except:
    pass

  if id:
    ret = f'#{id}'+'{'+ ";".join([key+":"+style[key] for key in style.keys()]) + '}'
  else:
    ret = ";".join([key+":"+style[key] for key in style.keys()])
  config["styleSheetList"].append(ret)
  style_str = '\n'.join(config["styleSheetList"])
  widget.setStyleSheet(style_str)


def cascading_styles(*args):
  """
  级联样式
  """
  style = {}
  for arg in args:
    if isinstance(arg, dict):
      for key in arg.keys():
        style[key] = arg[key]
    else:
      pass
  return style

def s2t(*args):
  """
  将样式字典转换为样式字符串 style to text
  """
  style = cascading_styles(*args)
  return ";".join([key+":"+style[key] for key in style.keys()])
