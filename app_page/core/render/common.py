# 组件类型别名映射
aliasWidgetMap = {
  # 基础组件
  'div': 'QWidget',
  'widget': 'QWidget',
  'label': 'QLabel',
  'button': 'QPushButton',
  'line-edit': 'QLineEdit',
  'text-edit': 'QPlainTextEdit',
  'selector': 'QComboBox',
  'checkbox': 'QCheckBox',
  'radio': 'QRadioButton',
  # 布局相关
  'grid': 'QGridLayout',
  'h-box': 'QHBoxLayout',
  'v-box': 'QVBoxLayout',
  'form': 'QFormLayout',
  'stacked': 'QStackedLayout',
  'graphics-anchor': 'QGraphicsAnchorLayout',
  'graphics-grid': 'QGraphicsGridLayout',
  'graphics-layout': 'QGraphicsLayout',
  'graphics-linear': 'QGraphicsLinearLayout',
}


def getWidget(tag_name:str):
  return aliasWidgetMap[tag_name] if tag_name in aliasWidgetMap else tag_name