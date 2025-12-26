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
        self.playlist: list[dict] = []  # [{'url': str, 'name': str}, ...]
        self.current_index: int = -1
        self.position: int = 0
        self.duration: int = 0
        self.play_history: set[int] = set()  # 用于随机模式避免重复
        self.is_source_set = False  # 新增：是否已为当前歌曲设置过源

    def load_from_folder(self, folder_path: str) -> int:
        self.playlist.clear()
        self.play_history.clear()
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
        """顺序播放：下一首"""
        if not self.has_songs():
            return -1
        return (self.current_index + 1) % len(self.playlist)

    def next_index_shuffle(self) -> int:
        """随机播放：随机选择一首未播放过的，如果全部播放过则重置"""
        if not self.has_songs():
            return -1

        available = set(range(len(self.playlist))) - self.play_history
        if not available:
            # 全部播放过，重置历史
            self.play_history.clear()
            available = set(range(len(self.playlist)))

        next_idx = random.choice(list(available))
        self.play_history.add(next_idx)
        return next_idx

    def set_index(self, index: int):
        if not self.has_songs():
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
        self.player.errorOccurred.connect(self._on_error)

        self.play_mode: PlayMode = PlayMode.REPEAT_ALL  # 默认顺序播放

    # ================== 播放模式控制 ==================

    def set_play_mode(self, mode: PlayMode):
        """设置播放模式"""
        self.play_mode = mode
        # 随机模式时重置播放历史
        if mode == PlayMode.SHUFFLE:
            self.music.play_history.clear()

    def toggle_play_mode(self) -> PlayMode:
        """循环切换播放模式"""
        modes = [PlayMode.REPEAT_ONE, PlayMode.REPEAT_ALL, PlayMode.SHUFFLE]
        current_idx = modes.index(self.play_mode)
        next_idx = (current_idx + 1) % len(modes)
        self.play_mode = modes[next_idx]
        if self.play_mode == PlayMode.SHUFFLE:
            self.music.play_history.clear()
        return self.play_mode

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
            self.music.current_index = 0
            if self.play_mode == PlayMode.SHUFFLE:
                self.music.play_history.clear()
        else:
            self.music.current_index = -1
        self._set_source()
        return count

    def play(self):
        if not self.music.has_songs():
            return
        # 只在必要时设置源（第一次播放当前歌曲或切换歌曲时）
        if not self.music.is_source_set:
            if not self._set_source():
                return
            self.music.is_source_set = True
        self.player.play()

    def pause(self):
        self.player.pause()
        self.music.position = self.player.position()  # 更新保存的位置

    def stop(self):
        self.music.position = 0  # 停止时重置位置（可选，根据需求）
        self.player.stop()

    def next(self):
        if not self.music.has_songs():
            return
        self._choose_next_song()
        self.music.is_source_set = False  # 切换歌曲 → 需要重新设置源
        self.music.position = 0           # 切换歌曲时通常从头开始
        self._set_source()
        self.player.play()

    def prev(self):
        """上一首：无论何种模式，总是按列表顺序上一首"""
        if not self.music.has_songs():
            return
        self.music.current_index = (self.music.current_index - 1) % len(self.music.playlist)
        self.music.is_source_set = False  # 切换歌曲 → 需要重新设置源
        self.music.position = 0
        self._set_source()
        self.player.play()

    def _choose_next_song(self):
        """根据当前播放模式决定下一首"""
        if self.play_mode == PlayMode.REPEAT_ONE:
            # 单曲循环：保持当前索引
            pass
        elif self.play_mode == PlayMode.REPEAT_ALL:
            # 列表循环：顺序下一首
            self.music.current_index = self.music.next_index_sequence()
        elif self.play_mode == PlayMode.SHUFFLE:
            # 随机播放
            self.music.current_index = self.music.next_index_shuffle()
        else:
            print('未知播放模式')

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

    def _set_source(self) -> bool:
        url = self.music.get_current_url()
        if not url:
            return False
        self.player.setSource(QUrl.fromLocalFile(url))
        return True

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
        if state == QMediaPlayer.StoppedState:
            # 判断是否自然播放结束（有一定容差）
            if self.music.position >= self.music.duration - 500:
                if self.play_mode == PlayMode.REPEAT_ONE:
                    self.music.is_source_set = False
                    self.music.position = 0
                    self._set_source()
                    self.player.play()
                elif self.play_mode == PlayMode.REPEAT_ALL:
                    self.next()
                elif self.play_mode == PlayMode.SHUFFLE:
                    self.next()
        self.seek(self.music.position)
        if state in [QMediaPlayer.PlayingState, QMediaPlayer.PausedState]:
            self._notify_update()

    @Slot(QMediaPlayer.Error, str)
    def _on_error(self, error, error_string):
        print(f"播放器错误: {error} - {error_string}")
        self.callback.run('onError', error, error_string)

    def _notify_update(self):
        """通知 UI 更新"""
        self.callback.run('rerender', self.music.current_index, self.music.position)