import sys

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice

def loadUI(filePath, target=None):
  ui_file = QFile(filePath)
  if not ui_file.open(QIODevice.ReadOnly):
    print(f"cannot open {filePath}")
    sys.exit(-1)
  if target:
    return QUiLoader(target).load(ui_file)
  else:
    return QUiLoader().load(ui_file)