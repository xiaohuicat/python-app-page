from . import global_variable as glv

class Store:
  def __init__(self, dict=None):
    if dict:
      glv._init()
      glv.GLOBALS_DICT = dict

  def set(self, key, value):
    """设置值"""
    if isinstance(key, str):
      glv.set(key, value)
    elif isinstance(key, dict):
      for each in key.keys():
        glv.set(each, key[each])
    else:
      raise TypeError("key must be str or dict")

  def setDict(self, setDict:dict):
    """设置字典"""
    if isinstance(setDict, dict):
      glv.GLOBALS_DICT = setDict
      
  def get(self, key:str, default=None):
    """获取值"""
    return glv.get(key, default)
  
  def has(self, key:str):
    """判断是否存在"""
    return key in glv.GLOBALS_DICT
  
  def getDict(self):
    """获取字典"""
    return glv.GLOBALS_DICT
  
  def print(self, key:str):
    """打印参数"""
    return glv.printParam(key)
  
  def keys(self):
    """获取所有键"""
    return list(glv.GLOBALS_DICT.keys())
  
  def values(self):
    """获取所有值"""
    return list(glv.GLOBALS_DICT.values())
  
  def remove(self, key=None):
    """移除指定值或所有值"""
    if not key:
      glv.GLOBALS_DICT = {}
    else:
      del glv.GLOBALS_DICT[key]