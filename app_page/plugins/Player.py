from enum import Enum, auto
import random
from pathlib import Path
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, Slot
from app_page import Callback


class PlayMode(Enum):
    REPEAT_ONE = auto()    # 单曲循环
    REPEAT_ALL = auto()    # 列表循环
    SHUFFLE = auto()       # 随机播放


class Music:
    """管理播放列表和当前播放信息"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.playlist: list[dict] = []
        self.current_index: int = -1
        self.position: int = 0
        self.duration: int = 0
        self.play_history: set[int] = set()

    def load_from_folder(self, folder_path: str) -> int:
        self.playlist.clear()
        self.play_history.clear()
        self.current_index = -1
        self.position = 0

        path = Path(folder_path)
        if not path.is_dir():
            return 0

        supported = ('.mp3', '.wav', '.ogg', '.flac')
        for file in path.iterdir():
            if file.is_file() and file.suffix.lower() in supported:
                self.playlist.append({
                    'url': str(file),
                    'name': file.name
                })

        return len(self.playlist)

    def has_songs(self) -> bool:
        return len(self.playlist) > 0

    def get_current_url(self) -> str | None:
        if not self.has_songs() or self.current_index < 0:
            return None
        return self.playlist[self.current_index]['url']

    def get_current_name(self) -> str:
        if not self.has_songs() or self.current_index < 0:
            return "暂无歌曲"
        return self.playlist[self.current_index]['name']

    def next_index_sequence(self) -> int:
        if not self.has_songs():
            return -1
        return (self.current_index + 1) % len(self.playlist)

    def next_index_shuffle(self) -> int:
        if not self.has_songs():
            return -1

        available = set(range(len(self.playlist))) - self.play_history
        if not available:
            self.play_history.clear()
            available = set(range(len(self.playlist)))

        next_idx = random.choice(list(available))
        self.play_history.add(next_idx)
        return next_idx

    def set_index(self, index: int):
        if not self.has_songs() or index < 0:
            return
        self.current_index = index % len(self.playlist)


class Player:
    def __init__(self):
        self.callback = Callback()
        self.music = Music()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        self.player.errorOccurred.connect(self._on_error)

        self.play_mode: PlayMode = PlayMode.REPEAT_ALL

    # ================== 播放模式控制 ==================

    def set_play_mode(self, mode: PlayMode):
        if mode == PlayMode.SHUFFLE:
            self.music.play_history.clear()
        elif self.play_mode == PlayMode.SHUFFLE:
            # 从随机切走时也清理历史
            self.music.play_history.clear()
        self.play_mode = mode

    def toggle_play_mode(self) -> PlayMode:
        modes = [PlayMode.REPEAT_ONE, PlayMode.REPEAT_ALL, PlayMode.SHUFFLE]
        current_idx = modes.index(self.play_mode)
        next_idx = (current_idx + 1) % len(modes)
        new_mode = modes[next_idx]
        self.set_play_mode(new_mode)
        return new_mode

    def get_play_mode_name(self) -> str:
        names = {
            PlayMode.REPEAT_ONE: "单曲循环",
            PlayMode.REPEAT_ALL: "列表循环",
            PlayMode.SHUFFLE: "随机播放"
        }
        return names.get(self.play_mode, "未知模式")

    # ================== 播放控制 ==================

    def load_playlist(self, folder_path: str) -> int:
        count = self.music.load_from_folder(folder_path)
        if count > 0:
            self.music.set_index(0)  # 自动选中第一首
        self._notify_update()
        return count
    
    def setPosition(self, position_ms: int):
        self.player.setPosition(position_ms)

    def play(self):
        if not self.music.has_songs():
            return

        if self.music.get_current_url() is None:
            return

        # 如果当前歌曲还没加载源，或者源不对，则重新设置
        if self.player.source().toLocalFile() != self.music.get_current_url():
            self.player.setSource(QUrl.fromLocalFile(self.music.get_current_url()))

        self.player.play()

    def pause(self):
        self.player.pause()
        self.music.position = self.player.position()

    def stop(self):
        self.music.position = 0
        self.player.stop()

    def next(self):
        if not self.music.has_songs():
            return
        self._choose_next_song()
        self._play_current_from_start()

    def prev(self):
        if not self.music.has_songs():
            return
        prev_idx = (self.music.current_index - 1) % len(self.music.playlist)
        self.music.set_index(prev_idx)
        self._play_current_from_start()

    # 新增：通过索引直接播放某首歌（用户点击列表时调用）
    def playByIndex(self, index: int):
        if not self.music.has_songs() or index < 0 or index >= len(self.music.playlist):
            return
        # 如果是同一首歌且正在播放，不重复加载
        if index == self.music.current_index and self.player.playbackState() == QMediaPlayer.PlayingState:
            return

        self.music.set_index(index)
        self._play_current_from_start()

    def _play_current_from_start(self):
        """切换到当前索引的歌曲并从头播放"""
        self.music.position = 0
        url = self.music.get_current_url()
        if url:
            self.player.setSource(QUrl.fromLocalFile(url))
            self.player.setPosition(0)
            self.player.play()
        self._notify_update()

    def _choose_next_song(self):
        if self.play_mode == PlayMode.REPEAT_ONE:
            return  # 保持当前
        elif self.play_mode == PlayMode.REPEAT_ALL:
            self.music.current_index = self.music.next_index_sequence()
        elif self.play_mode == PlayMode.SHUFFLE:
            self.music.current_index = self.music.next_index_shuffle()

    def seek(self, position_ms: int):
        if position_ms < 0:
            position_ms = 0
        self.player.setPosition(position_ms)

    def set_volume(self, volume: int):
        volume = max(0, min(100, volume))
        self.audio_output.setVolume(volume / 100.0)

    def get_volume(self) -> int:
        return int(self.audio_output.volume() * 100)

    def is_playing(self) -> bool:
        return self.player.playbackState() == QMediaPlayer.PlayingState

    # ================== 信号槽 ==================

    @Slot(int)
    def _on_position_changed(self, position: int):
        self.music.position = position
        self.callback.run('setPosition', position)

    @Slot(int)
    def _on_duration_changed(self, duration: int):
        self.music.duration = duration
        self.callback.run('setDuration', duration)

    @Slot(QMediaPlayer.PlaybackState)
    def _on_state_changed(self, state: QMediaPlayer.PlaybackState):
        print('_on_state_changed:', state)
        self._notify_update()

    @Slot(QMediaPlayer.MediaStatus)
    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus):
        if status == QMediaPlayer.EndOfMedia:
            # 自然播放结束
            if self.play_mode == PlayMode.REPEAT_ONE:
                self._play_current_from_start()
            else:
                self.next()

    @Slot(QMediaPlayer.Error, str)
    def _on_error(self, error, error_string):
        print(f"播放器错误: {error} - {error_string}")
        self.callback.run('onError', error, error_string)

    def _notify_update(self):
        """通知 UI 更新当前歌曲和进度"""
        self.callback.run('rerender', self.music.current_index, self.music.position)