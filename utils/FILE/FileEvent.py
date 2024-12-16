import os
def existFolder(filePath):
  folder = os.path.dirname(filePath)
  if not os.path.exists(folder):
    os.makedirs(folder)