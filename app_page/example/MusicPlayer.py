import os
from PySide6.QtWidgets import QFileDialog, QSlider, QWidget
from PySide6.QtCore import Qt, QDir
from app_page_core import Param
from app_page.core import Page
from app_page.utils import assetsUrl, d2t, get_system_volume, encode, empty_container_qss, empty_container_xml
from app_page.plugins import Player, PlayMode
from app_page.animation.ScrollMethod import smoothScroll
from app_page.utils.date_time import format_milliseconds


ICON_BUTTON_STYLE = {
  'font-size': '16px',
  'border-radius': '8px',
  'background-color': '#f0f0f0',
}


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
        <v-box scroll="${music_scroll_option}">
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
          <button id="openFolder" width="24" height="24" class="operation-btn import"/>
          <button id="playMode" width="24" height="24" class="operation-btn ${playMode}"/>
          <button id="previous" width="24" height="24" class="operation-btn previous"/>
          <button id="startStop" width="24" height="24" class="operation-btn ${'pause' if isRunning else 'start'}"/>
          <button id="next" width="24" height="24" class="operation-btn next"/>
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
.operation-btn {
  border-radius: 6px;
  background-color: transparent;
}
.operation-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
}
.operation-btn.import {
  background-image: url("""+ assetsUrl('icon', 'player', 'import.png') +""");
}
.operation-btn.repeat_all {
  background-image: url("""+ assetsUrl('icon', 'player', 'circle.png') +""");
}
.operation-btn.repeat_one {
  background-image: url("""+ assetsUrl('icon', 'player', 'circle1.png') +""");
}
.operation-btn.shuffle {
  background-image: url("""+ assetsUrl('icon', 'player', 'shuffle.png') +""");
}
.operation-btn.previous {
  background-image: url("""+ assetsUrl('icon', 'player', 'left.png') +""");
}
.operation-btn.start {
  background-image: url("""+ assetsUrl('icon', 'player', 'start.png') +""");
}
.operation-btn.pause {
  background-image: url("""+ assetsUrl('icon', 'player', 'pause.png') +""");
}
.operation-btn.next {
  background-image: url("""+ assetsUrl('icon', 'player', 'right.png') +""");
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


class MusicPlayer(Page):
  def __init__(self):
    super().__init__('music-player')
    self.template:str = template
    self.style:str = STYLE
    self.slider:QSlider = None
    self.player:Player = None
    self.reject_update = False


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
      'playMode': self.getPlayMode(),
      'current': player.music.current_index,
      'playlist': player.music.playlist,
      'isRunning': player.is_playing(),
      'music_scroll_option': d2t({'id': 'music_scroll_area'}),
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
    scroll_value = self.localStore.get('scroll_value', -1)
    self.setTimeout(lambda *args: smoothScroll(self.getWidget('music_scroll_area'), 'vertical', scroll_value), 0.1)


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
    if self.reject_update:
      return
    # 没有self.player的时候直接保存数据
    self.setGlobal('index', index)
    self.setGlobal('position', position)
    if not self.player:
      return
    scroll_value = self.getWidget('music_scroll_area').verticalScrollBar().value()
    self.localStore.set('scroll_value', scroll_value)
    # 有self.player的时候重新刷新页面
    self.rerender({
      'encode': encode,
      'playMode': self.getPlayMode(),
      'current': self.player.music.current_index,
      'playlist': self.player.music.playlist,
      'isRunning': self.player.is_playing(),
      'music_scroll_option': d2t({'id': 'music_scroll_area'}),
    })
    self.show()


  def setValue(self, value):
    if self.reject_update:
      return
    self.setGlobal('position', value)
    if not self.slider:
      return
    scroll_value = self.getWidget('music_scroll_area').verticalScrollBar().value()
    self.localStore.set('scroll_value', scroll_value)
    self.slider.setValue(value)
    self.updateStartEndTime()


  def setRange(self, value):
    if self.reject_update:
      return
    self.setGlobal('range_max', value)
    if not self.slider:
      return
    self.slider.setRange(0, value)


  def updateStartEndTime(self):
    self.getWidget('startTime').setText(format_milliseconds(self.player.music.position))
    self.getWidget('endTime').setText(format_milliseconds(self.player.music.duration))


  def startStop(self):
    if self.player.is_playing():
      self.setClass('startStop', 'operation-btn start')
      self.player.pause()
    else:
      volume = get_system_volume()
      def play():
        print('播放音乐')
        if len(self.player.music.playlist) <= 0:
          self.tips('请导入音乐', 'warning')
          return
        try:
          self.reject_update = True
          position = self.player.music.position
          self.player.play()
          def delay():
            self.setClass('startStop', 'operation-btn pause')
            self.reject_update = False
            self.player.player.setPosition(position)
          self.setTimeout(lambda *args: delay(), 0.1)
        except Exception as error:
          self.reject_update = False
          self.tips('播放出错', 'fail')
          print('播放出错：', error)
  
      if volume > 0.8:
        self.tipsBox(topic='警告', title=f'当前音量为{int(volume*100)}%，是否播放', content='声音过大可能损坏听力', confirm=play)
      else:
        play()


  def getPlayMode(self):
    return PLAY_MODE_MAP[self.player.play_mode]


  def playModeToggle(self):
    self.player.toggle_play_mode()
    play_mode = self.getPlayMode()
    self.localStore.set('play_mode', play_mode)
    scroll_value = self.getWidget('music_scroll_area').verticalScrollBar().value()
    self.localStore.set('scroll_value', scroll_value)
    self.rerender({
      'encode': encode,
      'playModeIcon': play_mode,
      'current': self.player.music.current_index,
      'playlist': self.player.music.playlist,
      'isRunning': self.player.is_playing(),
      'music_scroll_option': d2t({'id': 'music_scroll_area'}),
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