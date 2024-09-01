from PySide6.QtWidgets import QWidget

def setWidgetStyle(widget:QWidget, style:dict|list, id=None, cover:bool = False):
  
  if isinstance(style, list):
    style = cascading_styles(*style)
  
  config = {"styleSheetList":[]}
  try:
    if not cover:
      config["styleSheetList"] = widget.styleSheet().split('\n')
  except:
    pass
  # print("styleSheetList:", config["styleSheetList"])
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

