import os
from PySide6.QtWidgets import QFileDialog, QSlider, QWidget
from PySide6.QtCore import Qt, QDir
from app_page_core import Param
from ..core import Page
from ..utils import assetsUrl, s2t, get_system_volume, encode, empty_container_qss, empty_container_xml
from ..plugins import Player, PlayMode
from ..utils.date_time import format_milliseconds


ICON_BUTTON_STYLE = {
  'font-size': '16px',
  'border-radius': '8px',
  'background-color': '#f0f0f0',
}

# 创建按钮
def createImgBtn(id, icon) -> str:
  url = assetsUrl('icon', 'player', icon)
  image_style = {
    'background-image': f'url({url})',
    'background-repeat': 'no-repeat',
    'background-position': 'center',
    'background-color': 'transparent',
  }
  return f'<button id="{id}" width="24" height="24" style="{s2t(ICON_BUTTON_STYLE, image_style)}"/>'


template = '''
<%
  currentFontWeight = lambda index: '600' if index == current else '400'
  currentFontSize = lambda index: '18px' if index == current else '14px'
  currentTextColor = lambda index: '#000' if index == current else '#666'
%>
<template>
  <div class="container">
    <v-box spacing="0" margins="[0,0,0,0]">
      <div>
        <v-box scroll="True">
          % if len(playlist) > 0:
            <div>
              <v-box align="AlignTop" margins="[0,0,0,0]">
              % for index, item in enumerate(playlist):
                <div height="25" style="color:${currentTextColor(index)};">
                  <v-box margins="[0,0,0,0]" >
                    <button
                      index="${index}"
                      text="${'.'.join(item['name'].split('.')[:-1])}"
                      height="20"
                      class="music-button"
                      style="font-size:${currentFontSize(index)};font-weight:{currentFontWeight(index)};" 
                      event-filter="play-music"
                    />
                  </v-box>
                </div>
              % endfor
              </v-box>
            </div>
          % else:
            ''' + empty_container_xml("暂无音乐，点击左下角导入音乐文件夹吧~") + '''
          % endif
        </v-box>
      </div>
      <div class="player-panel" height="45">
        <h-box spacing="10">
          ${createImgBtn('openFolder', 'import.png')}
          ${createImgBtn('playMode', playModeIcon)}
          ${createImgBtn('previous', 'left.png')}
          ${createImgBtn('startStop', 'pause.png' if isRunning else 'start.png')}
          ${createImgBtn('next', 'right.png')} 
          <QSlider id="slider" height="32" />
          <label id="startTime" text="0:00" />
          <label text="${encode('/')}" />
          <label id="endTime" text="0:00" />
        </h-box>
      </div>
    </v-box>
  </div>
</template>
'''

STYLE = """
.container {
  font-size: 16px;
  font-weight: bold;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.6);
}
.player-panel {
  background-color: #fff;
  border-radius: 8px;
}
#startTime, #endTime {
  font-weight:400;
  color:#666;
  font-size:13px;
}
.music-button {
  text-align:left;
}
.music-button:hover {
  color: #50C1FF;
}
""" + empty_container_qss()

PLAY_MODE = {
  'repeat_all': PlayMode.REPEAT_ALL, # 列表循环
  'repeat_one': PlayMode.REPEAT_ONE, # 单曲循环
  'shuffle': PlayMode.SHUFFLE, # 随机
}

PLAY_MODE_MAP = {
  PlayMode.REPEAT_ALL: 'repeat_all', # 列表循环
  PlayMode.REPEAT_ONE: 'repeat_one', # 单曲循环
  PlayMode.SHUFFLE: 'shuffle', # 随机
}


def isNum(value):
  return isinstance(value, (int, float))


def getPlayMode(playMode):
  if playMode == 'repeat_one':
    return 'circle1.png'
  elif playMode == 'repeat_all':
    return 'circle.png'
  else:
    return 'shuffle.png'


class MusicPlayer(Page):
  def __init__(self):
    super().__init__('music-player')
    self.template:str = template
    self.style:str = STYLE
    self.slider:QSlider = None
    self.player:Player = None


  def setup(self):
    self.onGlobalDestroy(self.saveGlobal)
  
    player = self.getPlayer()
    player.callback.remove()
    player.callback.add('rerender', self.render)
    player.callback.add('setPosition', self.setValue)
    player.callback.add('setDuration', self.setRange)
    player.callback.add('onError', lambda msg: self.tips(msg, 'fail'))
    self.player = player

    return {
      'encode': encode,
      'createImgBtn': createImgBtn,
      'playModeIcon': getPlayMode(self.getPlayMode()),
      'current': player.music.current_index,
      'playlist': player.music.playlist,
      'isRunning': player.is_playing(),
    }


  def getPlayer(self):
    if self.hasGlobal('player'):
      return self.getGlobal('player')
    else:
      player = Player()
      self.setGlobal('player', player)

      path = self.localStore.get("player_path", None)
      if path:
        player.load_playlist(path)

      play_mode = self.localStore.get('play_mode', 'repeat_all')
      player.set_play_mode(PLAY_MODE[play_mode if play_mode in PLAY_MODE.keys() else 'repeat_all'])
      
      index = self.getGlobal('index')
      position = self.getGlobal('position')
      range_max = self.getGlobal('range_max')

      player.music.current_index = index if isNum(index) else self.localStore.get('index', 0)
      player.music.position = position if isNum(position) else self.localStore.get('position', 0)
      player.music.duration = range_max if isNum(range_max) else self.localStore.get('range_max', 0)

      return player


  def hide(self, *args):
    self.player = None
    self.slider = None


  def show(self, *args):
    self.register('openFolder', 'clicked', self.importMusic)
    self.register('previous', 'clicked', self.prev)
    self.register('startStop', 'clicked', self.startStop)
    self.register('next', 'clicked', self.next)
    self.register('playMode', 'clicked', self.playModeToggle)
    self.regist_filter(self.click_filter)

    slider:QSlider = self.getWidget('slider')
    if slider and self.player:
      position = self.player.music.position
      range_max = self.player.music.duration
      slider.sliderMoved.connect(self.player.seek)
      slider.setOrientation(Qt.Horizontal)
      slider.setRange(0, range_max)
      slider.setValue(position)
      self.slider = slider

    self.updateStartEndTime()


  def importMusic(self):
    lastPath = self.localStore.get("player_path", QDir.currentPath())
    lastPath = os.path.dirname(lastPath)
    path = QFileDialog.getExistingDirectory(None, "选择音乐文件夹", lastPath)
    if path:
      self.player.load_playlist(path)
      self.player.music.current_index = 0
      self.localStore.set("player_path", path)
      self.clear()
      self.render(self.player.music.current_index, self.player.music.position)


  def click_filter(self, widget:QWidget):
    index = int(widget.property('index'))
    self.setGlobal('index', index)
    self.player.playByIndex(index)


  def prev(self):
    self.player.prev()

  
  def next(self):
    self.player.next()


  def render(self, index=-1, position=0):
    # 没有self.player的时候直接保存数据
    self.setGlobal('index', index)
    self.setGlobal('position', position)
    if not self.player:
      return
    # 有self.player的时候重新刷新页面
    self.rerender({
      'encode': encode,
      'createImgBtn': createImgBtn,
      'playModeIcon': getPlayMode(self.getPlayMode()),
      'current': self.player.music.current_index,
      'playlist': self.player.music.playlist,
      'isRunning': self.player.is_playing(),
    })
    self.show()


  def setValue(self, value):
    self.setGlobal('position', value)
    if not self.slider:
      return
    self.slider.setValue(value)
    self.updateStartEndTime()


  def setRange(self, value):
    self.setGlobal('range_max', value)
    if not self.slider:
      return
    self.slider.setRange(0, value)


  def updateStartEndTime(self):
    self.getWidget('startTime').setText(format_milliseconds(self.player.music.position))
    self.getWidget('endTime').setText(format_milliseconds(self.player.music.duration))


  def startStop(self):
    if self.player.is_playing():
      self.player.pause()
    else:
      volume = get_system_volume()
      if volume > 0.8:
        self.tipsBox(topic='警告', title=f'当前音量为{int(volume*100)}%，是否播放', content='声音过大可能损坏听力', confirm=lambda:self.player.play())
      else:
        if len(self.player.music.playlist) <= 0:
          self.tips('请导入音乐', 'warning')
          return
        print('播放音乐')
        try:
          self.player.play()
        except Exception as error:
          self.tips('播放出错', 'fail')
          print('播放出错：', error)


  def getPlayMode(self):
    return PLAY_MODE_MAP[self.player.play_mode]


  def playModeToggle(self):
    self.player.toggle_play_mode()
    play_mode = self.getPlayMode()
    self.localStore.set('play_mode', play_mode)
    self.rerender({
      'encode': encode,
      'createImgBtn': createImgBtn,
      'playModeIcon': getPlayMode(play_mode),
      'current': self.player.music.current_index,
      'playlist': self.player.music.playlist,
      'isRunning': self.player.is_playing(),
    })
    self.show()


  def saveGlobal(self):
    if not self.name:
      return
    path = self.getSoftwarePath("userPath", f"pages/{self.name}/config.json")
    localStore = Param(path, {})

    position = self.getGlobal('position')
    if isinstance(position, (int, float)):
      localStore.set('position', position)
    
    range_max = self.getGlobal('range_max')
    if range_max:
      localStore.set('range_max', range_max)
    
    index = self.getGlobal('index')
    if isinstance(index, (int, float)):
      localStore.set('index', index)
    
    localStore.save()


  def clear(self):
    self.setGlobal('index', 0)
    self.setGlobal('position', 0)
    self.setGlobal('range_max', 0)
    self.localStore.set('index', 0)
    self.localStore.set('position', 0)
    self.localStore.set('range_max', 0)