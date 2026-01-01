import sys, os, hashlib, subprocess
from pathlib import Path
from typing import Union


def get_file_md5(file_path: str) -> str:
    """计算文件的MD5哈希值"""
    md5_obj = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            md5_obj.update(chunk)
    return md5_obj.hexdigest()


def create_folder(dir_path):
    """
    创建文件夹（支持多层路径），路径存在则跳过
    
    Args:
        dir_path (str/Path): 要创建的文件夹路径，支持字符串或Path对象
    """
    # 将输入转换为Path对象，统一处理
    path = Path(dir_path)
    # exist_ok=True 表示路径存在时不报错，直接跳过
    # parents=True 表示支持创建多层父目录
    path.mkdir(parents=True, exist_ok=True)


def get_folder_size(folder_path: str, unit: str = "auto") -> Union[float, tuple]:
    """
    统计指定文件夹占用的磁盘空间
    
    Args:
        folder_path: 目标文件夹路径（绝对路径/相对路径均可）
        unit: 输出单位，可选值："B", "KB", "MB", "GB", "auto"（默认自动适配）
    
    Returns:
        如果 unit 为 "auto"，返回 (总大小, 最佳单位)；否则返回对应单位的数值
    """
    # 校验文件夹是否存在
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在：{folder_path}")
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"指定路径不是文件夹：{folder_path}")
    
    total_size = 0  # 总大小（字节）
    
    # 递归遍历文件夹中的所有文件和子文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # 获取文件大小（字节），并累加到总大小
                file_size = os.path.getsize(file_path)
                total_size += file_size
            except (PermissionError, FileNotFoundError, OSError) as e:
                # 跳过无权限访问或已被删除的文件
                print(f"无法读取文件 {file_path}：{str(e)}")
    
    # 单位转换
    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 **2,
        "GB": 1024** 3,
        "TB": 1024 **4
    }
    
    if unit == "auto":
        # 自动选择最合适的单位
        if total_size < units["KB"]:
            return total_size, "B"
        elif total_size < units["MB"]:
            return total_size / units["KB"], "KB"
        elif total_size < units["GB"]:
            return total_size / units["MB"], "MB"
        else:
            return total_size / units["GB"], "GB"
    else:
        # 按指定单位返回
        if unit not in units:
            raise ValueError(f"无效的单位！可选单位：{list(units.keys())}")
        return total_size / units[unit]


def clear_folder(folder_path: str, delete_subfolders: bool = False, confirm: bool = True) -> None:
    """
    删除指定文件夹内的所有文件，可选择是否删除子文件夹
    
    Args:
        folder_path: 目标文件夹路径（绝对路径/相对路径均可）
        delete_subfolders: 是否删除子文件夹，默认False（仅删文件，保留文件夹结构）
        confirm: 是否需要确认操作，默认True（防止误删）
    
    Raises:
        FileNotFoundError: 文件夹不存在
        NotADirectoryError: 指定路径不是文件夹
        PermissionError: 无操作权限
    """
    # 1. 基础校验
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在：{folder_path}")
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"指定路径不是文件夹：{folder_path}")
    
    # 2. 安全校验：防止误删根目录等关键目录
    critical_paths = ["/", "C:\\", "D:\\", "E:\\"]  # 可根据系统扩展
    normalized_path = os.path.normpath(folder_path).lower()
    if any(normalized_path == path.lower() for path in critical_paths):
        raise ValueError("禁止删除根目录等关键系统目录！")
    
    # 3. 确认操作（可选）
    if confirm:
        response = input(f"确认要清空文件夹 {folder_path} 吗？(y/n): ")
        if response.strip().lower() != "y":
            print("操作已取消")
            return
    
    # 4. 统计待删除内容（便于提示）
    file_count = 0
    folder_count = 0
    
    # 5. 遍历并删除文件/文件夹
    try:
        # 先删除文件（包括子文件夹内的文件）
        for root, dirs, files in os.walk(folder_path, topdown=False):
            # 删除当前目录下的所有文件
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    file_count += 1
                except (PermissionError, OSError) as e:
                    print(f"无法删除文件 {file_path}：{str(e)}")
            
            # 如果开启删除子文件夹，删除当前空文件夹
            if delete_subfolders:
                try:
                    os.rmdir(root)
                    folder_count += 1
                except (PermissionError, OSError) as e:
                    print(f"无法删除文件夹 {root}：{str(e)}")
        
        print(f"操作完成！成功删除 {file_count} 个文件")
        if delete_subfolders:
            print(f"成功删除 {folder_count} 个子文件夹")
    
    except Exception as e:
        raise RuntimeError(f"清空文件夹时发生错误：{str(e)}")
    

def open_folder(folder_path:str):
    """根据不同操作系统打开文件夹窗口"""
    if not os.path.isdir(folder_path):
        raise RuntimeError("路径无效，不是文件夹！")
    
    if sys.platform == "win32":
        os.startfile(folder_path)
    elif sys.platform == "darwin":
        subprocess.run(["open", folder_path], check=True)
    else:
        subprocess.run(["xdg-open", folder_path], check=True)


def delete_file(file_path):
    """
    根据文件路径删除文件，删除失败时抛出具体原因
    
    参数:
        file_path (str): 要删除的文件的完整路径
    
    异常:
        Exception: 包含删除失败具体原因的异常信息
    """
    # 先检查路径是否是文件（排除目录的情况）
    if not os.path.isfile(file_path):
        raise Exception(f"删除失败：路径 '{file_path}' 不是一个有效的文件，或文件不存在")
    
    try:
        # 执行删除操作
        os.remove(file_path)
        print(f"文件 '{file_path}' 已成功删除")
    except PermissionError:
        raise Exception(f"删除失败：没有权限删除文件 '{file_path}'，请检查文件权限")
    except IsADirectoryError:
        raise Exception(f"删除失败：路径 '{file_path}' 是一个目录，不是文件，无法用此方法删除")
    except FileNotFoundError:
        raise Exception(f"删除失败：文件 '{file_path}' 不存在")
    except OSError as e:
        # 捕获其他操作系统相关的异常（如文件被占用、路径非法等）
        raise Exception(f"删除失败：操作系统错误，原因：{e.strerror} (错误码: {e.errno})")
    except Exception as e:
        # 捕获其他未预期的异常
        raise Exception(f"删除失败：未知错误，原因：{str(e)}")
