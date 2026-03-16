"""
System Volume Control Utility
跨平台系统音量控制工具，支持Windows和macOS
"""

import sys, subprocess
import logging
from typing import Union, Optional
from ctypes import cast, POINTER

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VolumeControlError(Exception):
    """音量控制相关异常"""
    pass


class VolumeOutOfRangeError(VolumeControlError):
    """音量值超出范围异常"""
    pass


def _validate_level(level: float, min_val: float = 0.0, max_val: float = 1.0) -> None:
    """验证音量值是否在有效范围内"""
    if not (min_val <= level <= max_val):
        raise VolumeOutOfRangeError(f"音量值必须在{min_val}到{max_val}之间")


class WindowsVolumeController:
    """Windows系统音量控制器"""
    
    def __init__(self):
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        
        self.CLSCTX_ALL = CLSCTX_ALL
        self.AudioUtilities = AudioUtilities
        self.IAudioEndpointVolume = IAudioEndpointVolume
    
    def set_volume(self, level: float) -> None:
        """设置Windows音量
        
        Args:
            level: 音量值(0.0~1.0)
        """
        _validate_level(level)
        
        try:
            enumerator = self.AudioUtilities.GetDeviceEnumerator()
            default_speaker = enumerator.GetDefaultAudioEndpoint(0, 1)
            
            interface = default_speaker.Activate(
                self.IAudioEndpointVolume._iid_,
                self.CLSCTX_ALL,
                None
            )
            volume = cast(interface, POINTER(self.IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level, None)
            
            logger.info(f"Windows音量已设置为：{level * 100:.1f}%")
        except Exception as e:
            logger.error(f"设置Windows音量失败：{e}")
            raise VolumeControlError(f"设置音量失败：{e}")
    
    def get_volume(self) -> float:
        """获取Windows当前音量
        
        Returns:
            当前音量值(0.0~1.0)
        """
        try:
            enumerator = self.AudioUtilities.GetDeviceEnumerator()
            default_speaker = enumerator.GetDefaultAudioEndpoint(0, 1)
            
            interface = default_speaker.Activate(
                self.IAudioEndpointVolume._iid_,
                self.CLSCTX_ALL,
                None
            )
            volume = cast(interface, POINTER(self.IAudioEndpointVolume))
            current_level = volume.GetMasterVolumeLevelScalar()
            
            return round(current_level, 2)
        except Exception as e:
            logger.error(f"获取Windows音量失败：{e}")
            raise VolumeControlError(f"获取音量失败：{e}")
    
    def is_muted(self) -> bool:
        """检查是否静音"""
        try:
            enumerator = self.AudioUtilities.GetDeviceEnumerator()
            default_speaker = enumerator.GetDefaultAudioEndpoint(0, 1)
            
            interface = default_speaker.Activate(
                self.IAudioEndpointVolume._iid_,
                self.CLSCTX_ALL,
                None
            )
            volume = cast(interface, POINTER(self.IAudioEndpointVolume))
            return volume.IsMute() != 0
        except Exception as e:
            logger.error(f"检查静音状态失败：{e}")
            raise VolumeControlError(f"检查静音状态失败：{e}")
    
    def mute(self, muted: bool = True) -> None:
        """设置静音状态
        
        Args:
            muted: True为静音，False为取消静音
        """
        try:
            enumerator = self.AudioUtilities.GetDeviceEnumerator()
            default_speaker = enumerator.GetDefaultAudioEndpoint(0, 1)
            
            interface = default_speaker.Activate(
                self.IAudioEndpointVolume._iid_,
                self.CLSCTX_ALL,
                None
            )
            volume = cast(interface, POINTER(self.IAudioEndpointVolume))
            volume.SetMute(muted, None)
            
            logger.info(f"Windows{'已' if muted else '未'}静音")
        except Exception as e:
            logger.error(f"设置静音失败：{e}")
            raise VolumeControlError(f"设置静音失败：{e}")


class MacOSVolumeController:
    """macOS系统音量控制器"""
    
    def set_volume(self, level: int) -> None:
        """设置macOS音量
        
        Args:
            level: 音量值(0~100)
        """
        _validate_level(level / 100.0, 0.0, 1.0)
        
        try:
            script = f'set volume output volume {level}'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                raise VolumeControlError(f"设置音量失败：{result.stderr}")
            
            logger.info(f"macOS音量已设置为：{level}%")
        except subprocess.TimeoutExpired:
            logger.error("设置音量超时")
            raise VolumeControlError("设置音量超时")
        except Exception as e:
            logger.error(f"设置macOS音量失败：{e}")
            raise VolumeControlError(f"设置音量失败：{e}")
    
    def get_volume(self) -> float:
        """获取macOS当前音量
        
        Returns:
            当前音量值(0.0~1.0)
        """
        try:
            script = 'get volume settings'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                raise VolumeControlError(f"获取音量失败：{result.stderr}")
            
            # 解析输出结果
            for part in result.stdout.split(','):
                if 'output volume' in part:
                    volume_level = int(part.split(':')[-1].strip())
                    return round(volume_level / 100, 2)
            
            logger.warning("无法解析音量输出，返回默认值")
            return 0.0
            
        except subprocess.TimeoutExpired:
            logger.error("获取音量超时")
            raise VolumeControlError("获取音量超时")
        except Exception as e:
            logger.error(f"获取macOS音量失败：{e}")
            raise VolumeControlError(f"获取音量失败：{e}")
    
    def is_muted(self) -> bool:
        """检查是否静音"""
        try:
            script = 'do shell script "ioreg -lw0 | grep IOACPIPlatformState | grep \"Output Volume\""'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode != 0
        except Exception as e:
            logger.error(f"检查静音状态失败：{e}")
            raise VolumeControlError(f"检查静音状态失败：{e}")
    
    def mute(self, muted: bool = True) -> None:
        """设置静音状态
        
        Args:
            muted: True为静音，False为取消静音
        """
        try:
            script = 'set volume output muted true' if muted else 'set volume output muted false'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                raise VolumeControlError(f"设置静音失败：{result.stderr}")
            
            logger.info(f"macOS{'已' if muted else '未'}静音")
        except subprocess.TimeoutExpired:
            logger.error("设置静音超时")
            raise VolumeControlError("设置静音超时")
        except Exception as e:
            logger.error(f"设置macOS静音失败：{e}")
            raise VolumeControlError(f"设置静音失败：{e}")


class SystemVolumeController:
    """跨平台系统音量控制器"""
    
    _windows_controller: Optional[WindowsVolumeController] = None
    _macos_controller: Optional[MacOSVolumeController] = None
    
    @classmethod
    def get_controller(cls) -> Union[WindowsVolumeController, MacOSVolumeController]:
        """获取对应平台的控制器"""
        if sys.platform.startswith('win32'):
            if cls._windows_controller is None:
                cls._windows_controller = WindowsVolumeController()
            return cls._windows_controller
        elif sys.platform.startswith('darwin'):
            if cls._macos_controller is None:
                cls._macos_controller = MacOSVolumeController()
            return cls._macos_controller
        else:
            raise NotImplementedError(f"暂不支持该操作系统：{sys.platform}")
    
    @classmethod
    def set_volume(cls, level: float) -> None:
        """设置系统音量
        
        Args:
            level: 音量值(0.0~1.0)
        """
        controller = cls.get_controller()
        if isinstance(controller, MacOSVolumeController):
            controller.set_volume(int(level * 100))
        else:
            controller.set_volume(level)
    
    @classmethod
    def get_volume(cls) -> float:
        """获取系统音量
        
        Returns:
            当前音量值(0.0~1.0)
        """
        controller = cls.get_controller()
        return controller.get_volume()
    
    @classmethod
    def is_muted(cls) -> bool:
        """检查是否静音"""
        controller = cls.get_controller()
        return controller.is_muted()
    
    @classmethod
    def mute(cls, muted: bool = True) -> None:
        """设置静音状态
        
        Args:
            muted: True为静音，False为取消静音
        """
        controller = cls.get_controller()
        controller.mute(muted)


# 便捷函数
def set_windows_volume(level: float) -> None:
    """设置Windows音量（向后兼容）"""
    WindowsVolumeController().set_volume(level)


def set_macos_volume(level: int) -> None:
    """设置macOS音量（向后兼容）"""
    MacOSVolumeController().set_volume(level)


def set_system_volume(level: float) -> None:
    """设置系统音量（向后兼容）"""
    SystemVolumeController.set_volume(level)


def get_system_volume() -> float:
    """获取系统音量（向后兼容）"""
    return SystemVolumeController.get_volume()


if __name__ == "__main__":
    print("测试系统音量控制...")
    
    try:
        # 设置音量为50%
        print("\n--- 设置音量 ---")
        set_system_volume(0.5)
        
        # 获取并打印当前音量
        print("\n--- 获取音量 ---")
        current_vol = get_system_volume()
        print(f"当前系统音量：{current_vol * 100:.1f}%")
        
        # 测试静音功能
        print("\n--- 测试静音 ---")
        is_muted = SystemVolumeController.is_muted()
        print(f"当前静音状态：{is_muted}")
        
        print("\n所有测试完成！")
        
    except VolumeControlError as e:
        print(f"错误：{e}")
    except Exception as e:
        print(f"未知错误：{e}")
        import traceback
        traceback.print_exc()