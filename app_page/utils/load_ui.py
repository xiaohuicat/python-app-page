import os, sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from ..core import Setting


# 加载UI文件
def loadUI(filePath, target=None):
  ui_file = QFile(filePath)
  if not ui_file.open(QIODevice.ReadOnly):
    print(f"cannot open {filePath}")
    sys.exit(-1)
  if target:
    return QUiLoader(target).load(ui_file)
  else:
    return QUiLoader().load(ui_file)


# 从设置加载UI类
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