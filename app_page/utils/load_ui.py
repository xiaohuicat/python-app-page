import sys
from typing import Optional
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, QObject
from ..core import Setting


def loadUI(filePath: str, target: Optional[QObject] = None) -> QObject:
    """
    加载UI文件并返回UI对象
    
    Args:
        filePath: UI文件的路径
        target: 可选的父对象，用于设置UI的父级
        
    Returns:
        加载的UI对象
        
    Raises:
        FileNotFoundError: 如果UI文件不存在
        RuntimeError: 如果无法打开或加载UI文件
    """
    ui_file = QFile(filePath)
    if not ui_file.open(QIODevice.ReadOnly):
      print(f"cannot open {filePath}")
      sys.exit(-1)
    if target:
      return QUiLoader(target).load(ui_file)
    else:
      return QUiLoader().load(ui_file)


def setupUiFromSetting(self: QObject, key: str, defaultValue: Optional[str] = None):
    """
    从设置中加载UI类并设置到当前对象
    
    Args:
        self: 要设置UI的对象
        key: 设置键名
        defaultValue: 默认UI类名，如果设置中没有找到指定的键
        
    Returns:
        包装后的UI对象，支持字典式访问
    """
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