SETTING = {}

def getSetting(key=None, defaultValue=None):
  """获取配置"""
  return SETTING.get(key, defaultValue)

def applySetting(key:str|dict, value=None):
  """设置配置"""
  if isinstance(key, dict):
    keys = list(key.keys())
    for each in keys:
      SETTING[each] = key[each]
  else:
    SETTING[key] = value
    
  return SETTING