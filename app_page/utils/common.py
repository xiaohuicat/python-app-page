import os, sys, shutil
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtWidgets import QWidget
from app_page_core import Store
from ..core import Setting
from ..config import Config

def assetsPath(*args):
    """获取资源路径
    Args:
        args (tuple): 目录，文件名

    Returns:
        path (str): 资源绝对路径
    """
    is_debug = Setting.getSetting("IS_DEBUG", False)
    packagePath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", *args)
    appPath = os.path.join(os.getcwd(), "assets", *args)
    if not is_debug:
      # 确保目标目录的父目录存在
      os.makedirs(os.path.dirname(appPath), exist_ok=True)
      # 检查源路径是否存在
      if os.path.exists(packagePath):
        try:
          # 复制文件或目录
          if os.path.isfile(packagePath):
            shutil.copy(packagePath, appPath)
          else:
            shutil.copytree(packagePath, appPath, dirs_exist_ok=True)
        except Exception as e:
          raise SystemError("复制文件或目录时出错", e)
      else:
        print("源路径不存在:", packagePath)
      return appPath
    else:
      return packagePath


def loadUI(filePath, target=None):
  ui_file = QFile(filePath)
  if not ui_file.open(QIODevice.ReadOnly):
    print(f"cannot open {filePath}")
    sys.exit(-1)
  if target:
    return QUiLoader(target).load(ui_file)
  else:
    return QUiLoader().load(ui_file)


def setupUiFromSetting(self, key, defaultValue=None):
  UI = Setting.getSetting(key, defaultValue)
  # 可以通过[]访问属性的UI 类
  class DictTypeUi(UI):
    def __init__(self,*args,**kwargs):
      super().__init__(*args,**kwargs)
    def __getitem__(self,__name):
      return super().__getattribute__(__name)
    
  ui = DictTypeUi()
  ui.setupUi(self)
  return ui


# 根据参数设置样式
def setAppStyle(target):
  config = Config()
  setting = target.param.child(target.param.pathJoin("userPath", "setting.json"), config.default_theme)
  id = setting.get("skin/current_skin_id", "skin001")
  style = list(filter( lambda each: each['id'] == id, setting.get("skinStyle", config.default_theme['skinStyle'])))[0]
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