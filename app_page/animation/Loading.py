from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QGridLayout
from ..utils.APP.setWidgetStyle import setWidgetStyle
from ..utils.layout_clear import layout_clear

WHITE_STYLE = {
  "border-radius": "20px",
  "padding": "20px",
  "background-color": "#fff"
}
  
  
class Loading:
  def __init__(self, layout:QVBoxLayout|QHBoxLayout|QGridLayout):
    self.layout = layout
  def create(self):
    # 加载GIF文件
    movie = QMovie("./assets/loading.gif")
    # movie.setCacheMode(QMovie.CacheAll)
    movie.setSpeed(120)                    # 可调整播放速度，默认为100%
    movie.finished.connect(movie.start)    # 电影结束后重新开始播放
    movie.isValid() and movie.start()      # 开始播放GIF
    # 添加一个label
    loading = QLabel()
    loading.setScaledContents(True)
    loading.setMovie(movie)
    loading.setFixedHeight(300)
    loading.setFixedWidth(300)
    setWidgetStyle(loading, WHITE_STYLE)
    self.layout.addWidget(loading)
    self.movie = movie
    self.loading = loading
  
  def remove(self):
    try:
      print("remove loading")
      self.loading.setMovie(None)
      layout_clear(self.layout)
      self.movie.stop()
      self.movie.finished.disconnect()
      self.movie.deleteLater()
      self.movie = None
      self.layout = None
    except Exception as e:
      print("remove loading error",e)