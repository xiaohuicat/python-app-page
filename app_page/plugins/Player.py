import os
from app_page import Callback
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl


class Music:
    def __init__(self):
        self.reset()
    
    # 上一首
    def prev(self):
        if self.index > 0:
            self.index -= 1
        else:
            self.index = len(self.playList) - 1
        self.position = 0

    # 下一首
    def next(self):
        if self.index < len(self.playList) - 1:
            self.index += 1
        else:
            self.index = 0
        self.position = 0
    
    def reset(self):
        self.playList = []
        self.index = -1
        self.position = 0
        self.url = None
        self.duration = 0
        self.state = None

    def getUrl(self):
        if self.index == -1:
            self.index = 0
        self.url = self.playList[self.index]['url']
        return self.url


    def hasUrl(self) -> bool:
        return self.url != None
    

    def loadPlaylist(self, folder_path:str):
        self.playList.clear()
        if not os.path.exists(folder_path):
            return
        for file_name in os.listdir(folder_path):
            if file_name.endswith(('.mp3', '.wav', '.ogg')):
                file_path = os.path.join(folder_path, file_name)
                self.playList.append({'url': file_path, 'name': file_name})


class Player:
    def __init__(self) -> None:
        self.callback = Callback()
        self.__player = QMediaPlayer()
        self.__audioOutput = QAudioOutput()
        self.__player.setAudioOutput(self.__audioOutput)
        self.__player.positionChanged.connect(self.__positionChanged)
        self.__player.durationChanged.connect(self.__durationChanged)
        self.__player.playbackStateChanged.connect(self.__stateChanged)
        self.__player.errorOccurred.connect(self.__playerError)

        self.music = Music()
        self.auto_loop = False
        self.state = None
        self.playing = False
    
    def setAutoLoop(self, isLoop:bool):
        self.auto_loop = isLoop

    def loadPlayList(self, folder_path:str):
        self.music.reset()
        self.__player.stop()
        self.playing = False
        self.music.loadPlaylist(folder_path)
    
    def play(self):
        self.playing = True
        if not self.music.hasUrl():
            self.__setSource()
        self.__player.play()
        self.__rerender()
    
    def stop(self):
        self.playing = False
        self.__player.pause()
        self.__rerender()

    def prev(self):
        self.music.prev()
        self.__setSource()
        self.play()

    def next(self):
        self.music.next()
        self.__setSource()
        self.play()

    def setPosition(self, position:int):
        self.__player.setPosition(position)

    def setVolume(self, volume:int):
        if volume < 0:
            volume = 0
        elif volume > 100:
            volume = 100
        self.__audioOutput.setVolume(volume / 100)
    
    def getVolume(self) -> int:
        return int(self.__audioOutput.volume() * 100)
    
    def isPlaying(self) -> bool:
        return self.__player.playbackState() == QMediaPlayer.PlayingState
    
    def isPaused(self) -> bool:
        return self.__player.playbackState() == QMediaPlayer.PausedState
    
    def isStopped(self) -> bool:
        return self.__player.playbackState() == QMediaPlayer.StoppedState
    
    def __setSource(self):
        url = self.music.getUrl()
        self.__player.setSource(QUrl.fromLocalFile(url))

    def __positionChanged(self, position:int):
        self.music.position = position
        self.callback.run('setValue', position)

    def __durationChanged(self, duration:int):
        self.music.duration = duration
        self.callback.run('setRange', duration)

    def __stateChanged(self, state:str):
        self.state = state
        reachEnd = self.music.position == self.music.duration and state == QMediaPlayer.StoppedState
        if reachEnd and self.auto_loop:
            self.next()
            return
        self.setPosition(self.music.position)
        
    def __playerError(self, error, error_string):
        print('playerError:', error, error_string)

    def __rerender(self):
        self.callback.run('rerender', self.music.index, self.music.position)