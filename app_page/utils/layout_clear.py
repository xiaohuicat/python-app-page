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