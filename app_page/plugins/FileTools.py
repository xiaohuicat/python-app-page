import os
import hashlib
import zipfile
import platform
from typing import Dict, List, Optional, Callable
from PIL import Image, ImageDraw, ImageFont


class FileTools:
    def __init__(self, filePath: str) -> None:
        self.filePath: str = os.path.abspath(filePath)
        # 存储所有文件信息的字典，key为文件绝对路径，value为文件详细信息
        self.file_info_map: Dict[str, Dict] = {}
        # 标记是否已加载完成，避免重复加载
        self._loaded: bool = False
        # 存储总文件大小（字节）
        self._total_size: int = 0
        # 目录结构绘制的符号常量
        self._TREE_SYMBOLS = {
            'branch': '├── ',
            'last_branch': '└── ',
            'pipe': '│   ',
            'space': '    '
        }
        # 新增：预定义各系统的默认兼容字体（支持Unicode符号）
        self._SYSTEM_FONTS = {
            'Windows': ['msyh.ttc', 'simhei.ttf', 'simsun.ttc'],  # 微软雅黑、黑体、宋体
            'Darwin': ['PingFang SC.ttc', 'Hiragino Sans GB.ttc'],  # macOS 苹方、冬青黑
            'Linux': ['NotoSansCJK-Regular.ttc', 'SimHei.ttf', 'WenQuanYi Zen Hei']  # Linux 思源黑体、文泉驿
        }

    def load(self, option: Optional[Dict] = None) -> None:
        """
        唯一的目录遍历函数，加载所有文件信息到file_info_map
        :param option: 可选配置字典，支持的key：
                    - skip_folders: 列表，需要跳过的文件夹名称（如['__pycache__', '.git']）
                    - enable_md5: 布尔值，是否开启MD5计算（默认True）
        """
        if self._loaded:
            return  # 已加载过则直接返回，避免重复遍历

        # 初始化配置
        option = option or {}
        skip_folders = option.get('skip_folders', [])
        enable_md5 = option.get('enable_md5', False)
        
        # 容错处理
        if not isinstance(skip_folders, list):
            skip_folders = []
        if not isinstance(enable_md5, bool):
            enable_md5 = True

        # 转换为集合，提升查询效率
        skip_folders_set = set(skip_folders)
        
        self.file_info_map.clear()
        self._total_size = 0
        root_dir_name: str = os.path.basename(self.filePath)

        try:
            # 关键修复：使用topdown=True（默认），并修改dirs列表来跳过整个目录树
            for foldername, dirs, filenames in os.walk(self.filePath, topdown=True):
                # 核心修复：提前过滤文件夹，直接从dirs中移除，os.walk会跳过这些文件夹的遍历
                # 遍历dirs的副本，避免修改原列表导致的遍历异常
                for dir_name in list(dirs):
                    if dir_name in skip_folders_set:
                        dirs.remove(dir_name)  # 从遍历列表中移除，彻底跳过该文件夹及其子目录
                        print(f"跳过文件夹（递归）：{os.path.join(foldername, dir_name)}")

                # 处理当前文件夹下的文件
                for filename in filenames:
                    # 跳过需要忽略的文件（比如.DS_Store这类文件）
                    if filename in skip_folders_set:
                        print(f"跳过文件：{os.path.join(foldername, filename)}")
                        continue
                    
                    file_path: str = os.path.join(foldername, filename)
                    if not os.path.isfile(file_path):
                        continue

                    # 计算文件属性
                    size: int = os.path.getsize(file_path)
                    if enable_md5:
                        md5: str = _md5_file(file_path)
                    else:
                        md5: str = ""
                    ext: str = os.path.splitext(filename)[1].lower()
                    ret_path: str = os.path.relpath(file_path, self.filePath).replace("\\", "/")
                    ret_path = f"{root_dir_name}/{ret_path}"

                    # 存储文件信息
                    self.file_info_map[file_path] = {
                        "abs_path": file_path,
                        "ret_path": ret_path,
                        "md5": md5,
                        "size": size,
                        "ext": ext,
                        "filename": filename,
                        "folder": foldername
                    }
                    self._total_size += size

            self._loaded = True
            md5_status = "开启" if enable_md5 else "关闭"
            print(f"加载完成，共扫描 {len(self.file_info_map)} 个文件，总大小 {self._total_size/1024/1024:.2f} MB，MD5计算：{md5_status}")
        except Exception as e:
            print(f"遍历目录失败 {self.filePath}: {e}")
            self._loaded = False

    def get_all_size(self, unit: str = "byte") -> float:
        """
        获取所有文件的总大小
        :param unit: 单位，可选值：byte(字节)、kb(千字节)、mb(兆字节)、gb(吉字节)
        :return: 总大小（保留2位小数）
        """
        if not self._loaded:
            self.load()  # 懒加载：未加载则先执行load

        units = {
            "byte": 1,
            "kb": 1024,
            "mb": 1024 * 1024,
            "gb": 1024 * 1024 * 1024
        }

        if unit.lower() not in units:
            raise ValueError(f"不支持的单位：{unit}，可选单位：{list(units.keys())}")

        total = self._total_size / units[unit.lower()]
        return round(total, 2)

    def _build_dir_tree(self) -> Dict:
        """构建目录树的嵌套字典结构，为绘制做准备"""
        # 初始化根节点
        root_name = os.path.basename(self.filePath)
        dir_tree = {
            'name': root_name,
            'type': 'dir',
            'children': [],
            'path': self.filePath
        }

        # 遍历所有文件，构建目录树
        for file_path, file_info in self.file_info_map.items():
            # 获取相对根目录的路径片段
            rel_path = os.path.relpath(file_path, self.filePath)
            path_parts = rel_path.split(os.sep)
            
            # 从根节点开始，逐层创建目录节点
            current_node = dir_tree
            for i, part in enumerate(path_parts):
                # 最后一个部分是文件，其他是目录
                is_file = i == len(path_parts) - 1
                
                # 检查当前层级是否已存在该节点
                child_exists = False
                for child in current_node['children']:
                    if child['name'] == part:
                        current_node = child
                        child_exists = True
                        break
                
                if not child_exists:
                    # 创建新节点
                    new_node = {
                        'name': part,
                        'type': 'file' if is_file else 'dir',
                        'children': [],
                        'path': os.path.join(current_node['path'], part)
                    }
                    # 如果是文件，补充文件信息
                    if is_file:
                        new_node['size'] = file_info['size']
                        new_node['md5'] = file_info['md5']
                    
                    current_node['children'].append(new_node)
                    current_node = new_node

        return dir_tree

    def _generate_tree_text(self, show_size: bool = True, show_md5: bool = False) -> List[str]:
        """生成目录结构的文本行列表（供print和draw方法共用）"""
        tree_lines = []
        
        if not self.file_info_map:
            tree_lines.append(f"目录 {self.filePath} 下无文件")
            return tree_lines

        # 构建目录树
        dir_tree = self._build_dir_tree()
        
        # 添加标题行
        tree_lines.append(f"[DIR] {dir_tree['name']} (总大小: {self.get_all_size('mb')} MB)")
        tree_lines.append("└── " + ("─" * len(dir_tree['name'])))
        
        # 递归生成文本行
        def _generate_lines(node: Dict, prefix: str = "", is_last: bool = True, lines: List[str] = None):
            if lines is None:
                lines = []
            
            # 处理当前节点的前缀和符号
            if prefix:
                branch_symbol = self._TREE_SYMBOLS['last_branch'] if is_last else self._TREE_SYMBOLS['branch']
                line = f"{prefix}{branch_symbol}{node['name']}"
            else:
                # 根节点的子节点开始绘制
                line = f"{self._TREE_SYMBOLS['branch'] if not is_last else self._TREE_SYMBOLS['last_branch']}{node['name']}"
            
            # 补充文件信息
            if node['type'] == 'file':
                size_str = f" ({node['size']/1024:.2f} KB)" if show_size else ""
                md5_str = f" | MD5: {node['md5']}" if show_md5 and node['md5'] else ""
                line += size_str + md5_str
            
            lines.append(line)
            
            # 处理子节点的前缀
            child_count = len(node['children'])
            for idx, child in enumerate(node['children']):
                child_is_last = idx == child_count - 1
                # 计算子节点的前缀：如果当前节点不是最后一个，需要保留pipe符号
                new_prefix = prefix + (self._TREE_SYMBOLS['space'] if is_last else self._TREE_SYMBOLS['pipe'])
                _generate_lines(child, new_prefix, child_is_last, lines)
            
            return lines

        # 生成根节点子节点的文本行
        root_children = dir_tree['children']
        for idx, child in enumerate(root_children):
            _generate_lines(child, "", idx == len(root_children) - 1, tree_lines)
        
        return tree_lines

    def print(self, show_size: bool = True, show_md5: bool = False) -> None:
        """
        绘制README风格的文件目录结构
        :param show_size: 是否显示文件大小（默认显示）
        :param show_md5: 是否显示文件MD5（默认不显示，避免结构过长）
        """
        if not self._loaded:
            self.load()  # 懒加载：未加载则先执行load

        # 获取目录结构文本行并打印
        tree_lines = self._generate_tree_text(show_size, show_md5)
        text = "\n" + "\n".join(tree_lines)
        return text  # 返回文本，方便AI调用后获取结果

    def draw(self, output_path: str = None, show_size: bool = False, show_md5: bool = False, 
            font_path: str = None, font_size: int = 12, bg_color: str = "white", 
            text_color: str = "black", line_height: Optional[int] = None, 
            img_width: Optional[int] = None) -> str:
        """
        将目录结构绘制为PNG图片（修复符号显示问题，新增系统字体自动适配）
        :param output_path: 输出图片路径（默认：原目录名+_tree.png）
        :param show_size: 是否显示文件大小（默认显示）
        :param show_md5: 是否显示文件MD5（默认不显示）
        :param font_path: 字体文件路径（可选，优先级高于系统默认字体）
        :param font_size: 字体大小（默认12）
        :param bg_color: 背景颜色（默认white）
        :param text_color: 文字颜色（默认black）
        :param line_height: 行高（可选，默认 font_size + 3）
        :param img_width: 图片宽度（可选，默认根据文本宽度自动计算）
        :return: 生成的图片文件路径
        """
        if not self._loaded:
            self.load()  # 懒加载：未加载则先执行load

        # 生成目录结构文本
        tree_lines = self._generate_tree_text(show_size, show_md5)
        
        # 设置默认输出路径
        if output_path is None:
            output_path = os.path.join(os.path.dirname(self.filePath), 
                                    f"{os.path.basename(self.filePath)}_tree.png")
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        try:
            # 核心修改：加载字体（手动传参>系统默认>兜底默认）
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size, encoding='utf-8')
            else:
                font = _get_default_font(self._SYSTEM_FONTS, font_size)

            # 计算文本尺寸（优化：使用font.getlength，更准确的Unicode字符宽度计算）
            if line_height is None:
                line_height = font_size + 3  # 如果没有传入line_height，使用默认值

            # 如果指定了图片宽度，使用指定宽度，否则计算文本最大宽度
            if img_width is None:
                max_width = int(max([font.getlength(line) for line in tree_lines]))
            else:
                max_width = img_width

            total_height = int(sum([font.size + line_height for line in tree_lines]))

            # 添加边距
            padding = 25
            img_height = total_height + 2 * padding

            # 创建图片（RGB模式，支持彩色）
            img = Image.new('RGB', (max_width + 2 * padding, img_height), color=bg_color)
            draw = ImageDraw.Draw(img)

            # 绘制文本（优化：起始坐标微调，对齐更美观）
            y = padding + font_size // 2
            for line in tree_lines:
                draw.text((padding, y), line, font=font, fill=text_color, align='left')
                y += font.size + line_height

            # 保存图片（优化：设置PNG压缩级别，减小文件体积）
            img.save(output_path, 'PNG', compress_level=6)
            print(f"目录结构图片已生成：{output_path}")
            return output_path

        except Exception as e:
            print(f"生成图片失败：{e}")
            return ""

    def write(self, output_path: str = None, show_size: bool = False, show_md5: bool = False, 
            title: str = "目录结构") -> str:
        """
        将目录结构写入Markdown文件
        :param output_path: 输出md文件路径（默认：原目录名+_tree.md）
        :param show_size: 是否显示文件大小（默认显示）
        :param show_md5: 是否显示文件MD5（默认不显示）
        :param title: md文件中的标题（默认：目录结构）
        :return: 生成的md文件路径
        """
        if not self._loaded:
            self.load()  # 懒加载：未加载则先执行load

        # 生成目录结构文本
        tree_lines = self._generate_tree_text(show_size, show_md5)
        
        # 设置默认输出路径
        if output_path is None:
            output_path = os.path.join(os.path.dirname(self.filePath), 
                                        f"{os.path.basename(self.filePath)}_tree.md")
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        try:
            # 构建Markdown内容（添加标题、代码块包裹，保证格式美观）
            md_content = []
            # 添加标题（一级标题）
            md_content.append(f"# {title}")
            md_content.append("")  # 空行分隔
            # 目录结构用代码块包裹（markdown的```语法），保证符号不被转义
            md_content.append("```bash")
            md_content.extend(tree_lines)
            md_content.append("```")
            md_content.append("")  # 文件末尾空行
            # 合并为完整文本
            md_text = "\n".join(md_content)

            # 写入文件（指定utf-8编码，避免中文乱码）
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_text)
            
            print(f"Markdown文件已生成：{output_path}")
            return output_path

        except Exception as e:
            print(f"写入Markdown失败：{e}")
            return ""
    
    def walk(self, callback: Optional[Callable[[Dict], None]] = None) -> None:
        """遍历已加载的文件信息，执行回调函数（无需重复遍历目录）"""
        if not self._loaded:
            self.load()  # 懒加载：未加载则先执行load

        if not callback:
            return

        # 直接遍历已存储的文件信息，无需再次扫描目录
        for file_info in self.file_info_map.values():
            # 只返回原代码中回调需要的字段，保持接口兼容
            callback({
                "ret_path": file_info["ret_path"],
                "md5": file_info["md5"],
                "size": file_info["size"],
                "ext": file_info["ext"],
                "filename": file_info["filename"]
            })

    def zip(self) -> str:
        """压缩文件（使用已加载的文件信息，无需重复遍历目录）"""
        if not self._loaded:
            self.load()  # 懒加载：未加载则先执行load

        if not self.file_info_map:
            print("无文件可压缩")
            return ""

        # 生成压缩包路径
        zip_path: str = f"{self.filePath}.zip"
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                # 遍历已存储的文件信息，添加到压缩包
                for file_info in self.file_info_map.values():
                    # 计算压缩包内的相对路径（保持原目录结构）
                    arcname: str = os.path.relpath(file_info["abs_path"], self.filePath)
                    zipf.write(file_info["abs_path"], arcname)
            print(f"压缩完成，压缩包路径：{zip_path}")
            return zip_path
        except Exception as e:
            print(f"压缩失败 {zip_path}: {e}")
            # 清理失败的压缩包
            if os.path.exists(zip_path):
                os.remove(zip_path)
            return ""

    def get_all_files(self) -> List[Dict]:
        """获取所有文件信息的列表（便捷方法）"""
        if not self._loaded:
            self.load()
        return list(self.file_info_map.values())


def _md5_file(path: str) -> str:
    """计算文件的MD5值（分块读取，支持大文件）"""
    try:
        with open(path, 'rb') as f:
            md5 = hashlib.md5()
            # 按4096字节分块读取，避免一次性加载大文件到内存
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
            return md5.hexdigest()
    except Exception as e:
        print(f"计算MD5失败 {path}: {e}")
        return ""


def _get_default_font(system_fonts_map, font_size: int) -> ImageFont.FreeTypeFont:
    """新增：自动获取系统默认的支持Unicode的字体，解决符号显示问题"""
    system = platform.system()  # 获取系统类型：Windows/Darwin(Linux)/Linux
    font_candidates = system_fonts_map.get(system, system_fonts_map['Linux'])
    
    # 遍历候选字体，找到系统中存在的字体
    if system == 'Windows':
        font_dirs = [os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')]
    elif system == 'Darwin':
        font_dirs = ['/System/Library/Fonts', '/Library/Fonts', os.path.expanduser('~/Library/Fonts')]
    else:  # Linux
        font_dirs = ['/usr/share/fonts', '/usr/local/share/fonts', os.path.expanduser('~/.fonts')]

    # 查找可用字体文件
    font_file = None
    for dir_path in font_dirs:
        if not os.path.exists(dir_path):
            continue
        for font_name in font_candidates:
            f_path = os.path.join(dir_path, font_name)
            if os.path.exists(f_path):
                font_file = f_path
                break
    if font_file:
        try:
            return ImageFont.truetype(font_file, font_size, encoding='utf-8')
        except Exception:
            pass
    # 兜底：使用Pillow默认字体，开启抗锯齿
    return ImageFont.load_default(size=font_size)