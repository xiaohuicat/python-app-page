import sys
import subprocess
from ctypes import cast, POINTER

def set_windows_volume(level: float):
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    if not (0.0 <= level <= 1.0):
        raise ValueError("音量值必须在 0.0 到 1.0 之间")
    
    enumerator = AudioUtilities.GetDeviceEnumerator()
    default_speaker = enumerator.GetDefaultAudioEndpoint(0, 1)
    
    interface = default_speaker.Activate(
        IAudioEndpointVolume._iid_,
        CLSCTX_ALL,
        None
    )
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    
    volume.SetMasterVolumeLevelScalar(level, None)
    print(f"Windows 音量已设置为：{level * 100:.1f}%")


def set_macos_volume(level: int):
    if not (0 <= level <= 100):
        raise ValueError("音量值必须在 0 到 100 之间")
    
    script = f'set volume output volume {level}'
    subprocess.run(['osascript', '-e', script])
    print(f"macOS 音量已设置为：{level}%")


def set_system_volume(level: float):
    if sys.platform.startswith('win32'):
        set_windows_volume(level)
    elif sys.platform.startswith('darwin'):
        set_macos_volume(int(level * 100))
    else:
        raise NotImplementedError("暂不支持该操作系统")


def get_system_volume() -> float:
    """
    获取当前系统音量（返回0.0~1.0之间的浮点数）
    """
    if sys.platform.startswith('win32'):
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        # Windows系统获取音量
        enumerator = AudioUtilities.GetDeviceEnumerator()
        default_speaker = enumerator.GetDefaultAudioEndpoint(0, 1)
        
        interface = default_speaker.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        # 获取当前音量（0.0~1.0）
        current_level = volume.GetMasterVolumeLevelScalar()
        return round(current_level, 2)  # 保留两位小数
    
    elif sys.platform.startswith('darwin'):
        # macOS系统获取音量
        # 通过AppleScript获取当前音量
        script = 'get volume settings'
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        # 解析输出结果（格式类似：output volume 50, input volume 0, alert volume 50, output muted false）
        for part in result.split(','):
            if 'output volume' in part:
                volume_level = int(part.split(':')[-1].strip())
                return round(volume_level / 100, 2)  # 转换为0.0~1.0范围并保留两位小数
        
        # 解析失败时返回0.0
        return 0.0
    
    else:
        raise NotImplementedError("暂不支持该操作系统")


# 测试代码
if __name__ == "__main__":
    # 设置音量为50%
    set_system_volume(0.5)
    # 获取并打印当前音量
    current_vol = get_system_volume()
    print(f"当前系统音量：{current_vol * 100:.1f}%")