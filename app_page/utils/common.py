import os, sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtWidgets import QWidget
from app_page_core import Store
from ..config import default_theme

def assetsPath(*args):
    """获取资源路径
    Args:
        args (tuple): 目录，文件名

    Returns:
        path (str): 资源绝对路径
    """
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", *args)


def loadUI(filePath, target=None):
  ui_file = QFile(filePath)
  if not ui_file.open(QIODevice.ReadOnly):
    print(f"cannot open {filePath}")
    sys.exit(-1)
  if target:
    return QUiLoader(target).load(ui_file)
  else:
    return QUiLoader().load(ui_file)


# 根据参数设置样式
def setAppStyle(target):
  setting = target.param.child(target.param.pathJoin("userPath", "setting.json"), default_theme)
  current = setting.get("skin/current_skin_index", 0)
  style = setting.get("skinStyle", default_theme['skinStyle'])[current]
  setWidgetStyleById(id='frame_header', style={"background-color": style['header_bg_color']}, cover=True)
  setWidgetStyleById(id='frame_main', style={
    "background-color": style['main_bg_color'],
    "border-image": f"url('{style['app_bg_image'].replace('\\', '/')}') stretch"
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


def layout_clear(layout):
  while layout.count():
    child = layout.takeAt(0)
    if child.widget() is not None:
      # print("delete widget", child.widget())
      child.widget().deleteLater()
    elif child.layout() is not None:
      # layout_clear(child.layout())
      print("delete layout", child.layout())
      child.layout().deleteLater()