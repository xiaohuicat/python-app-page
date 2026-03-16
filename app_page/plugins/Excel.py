import os
import logging
import tempfile
from typing import Optional, Dict, List, Union
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.drawing.image import Image as XLImage
from PIL import Image

# 配置日志
def _setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = _setup_logger(__name__)

# 常量定义
DPI_DEFAULT = 96
POINTS_PER_INCH = 72
CM_PER_INCH = 2.54
CELL_PADDING = 2
COLUMN_SCALE_FACTOR = 1.2

class Transform:
    """单位转换工具类"""
    
    def __init__(self, pixels: int = 0):
        self._pixels = pixels
        
    @property
    def pixels(self) -> int:
        return self._pixels
    
    @pixels.setter
    def pixels(self, value: int):
        self._pixels = value
    
    def pixels_to_points(self, dpi: int = DPI_DEFAULT) -> float:
        """像素转磅"""
        inches = self._pixels / dpi
        return inches * POINTS_PER_INCH
    
    def points_to_cm(self, points: Optional[float] = None) -> float:
        """磅转厘米"""
        if points is None:
            points = self.pixels_to_points()
        inches = points / POINTS_PER_INCH
        return inches * CM_PER_INCH
    
    def pixels_to_cm(self, dpi: int = DPI_DEFAULT) -> float:
        """像素转厘米"""
        points = self.pixels_to_points(dpi)
        return self.points_to_cm(points)
    
    def cm_to_pixels(self, cm: float, dpi: int = DPI_DEFAULT) -> int:
        """厘米转像素"""
        inches = cm / CM_PER_INCH
        points = inches * POINTS_PER_INCH
        return int(points * dpi / POINTS_PER_INCH)
    
    @property
    def cm(self) -> float:
        return self.pixels_to_cm()
    
    @cm.setter
    def cm(self, value: float):
        self._pixels = self.cm_to_pixels(value)
    
    @property
    def points(self) -> float:
        return self.pixels_to_points()
    
    @points.setter
    def points(self, value: float):
        self._pixels = int(value * DPI_DEFAULT / POINTS_PER_INCH)


def fill(color: str) -> PatternFill:
    """创建填充样式"""
    return PatternFill(start_color=color, end_color=color, fill_type='solid')


def get_column_name(cell_position: str) -> str:
    """从单元格位置提取列名"""
    return ''.join(filter(str.isalpha, cell_position))


def get_resize_image_path(image_path: str, width: int, height: int) -> str:
    """获取调整大小后的图片临时路径"""
    try:
        image = Image.open(image_path)
        image.thumbnail((width, height), Image.Resampling.LANCZOS)
        temp_dir = tempfile.gettempdir()
        name = os.path.basename(image_path)
        # 使用唯一文件名避免冲突
        import uuid
        unique_name = f"{uuid.uuid4().hex}_{name}"
        temp_file_path = os.path.join(temp_dir, unique_name)
        image.save(temp_file_path)
        return temp_file_path
    except Exception as e:
        logger.error(f"图片调整失败: {e}")
        raise


class Excel:
    """Excel操作封装类"""
    
    # 预定义颜色映射
    COLOR_MAP = {
        'red': 'ff0000',
        'green': '0cb336',
        'yellow': 'FFFF00',
        'blue': '0000ff',
        'black': '333333'
    }
    
    def __init__(self, file_path: Optional[str] = None):
        """
        初始化Excel对象
        :param file_path: Excel文件路径
        """
        self.file_path = file_path
        self.work_book: Optional[Workbook] = None
        self.work_sheet = None
        self.cell_data = None
        self._cell_max_len_dict: Dict[str, int] = {}
        self._temp_files: List[str] = []  # 追踪临时文件用于清理
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出，清理临时文件"""
        self._cleanup_temp_files()
    
    def _cleanup_temp_files(self):
        """清理临时文件"""
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.warning(f"删除临时文件失败: {e}")
        self._temp_files.clear()
    
    def load(self, file_path: Optional[str] = None, data_only: bool = False) -> 'Excel':
        """
        加载Excel文件
        :param file_path: 文件路径，不传则使用构造函数传入的路径
        :param data_only: 是否只加载数据
        :return: 当前实例
        """
        path = file_path or self.file_path
        if path and os.path.exists(path):
            self.work_book = op.load_workbook(path, data_only=data_only)
            self.file_path = path
        else:
            self.work_book = Workbook()
            self.file_path = None
        self.work_sheet = self.work_book.active
        return self
    
    def sheet(self, name: str = '', create: bool = False) -> 'Excel':
        """
        选择工作表
        :param name: 工作表名称，空则为活动工作表
        :param create: 如果不存在是否创建
        :return: 当前实例
        """
        if name == '':
            self.work_sheet = self.work_book.active
        elif name in self.work_book.sheetnames:
            self.work_sheet = self.work_book[name]
        elif create:
            self.work_sheet = self.work_book.create_sheet(name)
        else:
            raise ValueError(f"工作表 '{name}' 不存在")
        return self
    
    def cell(self, row: Union[int, str], column: Optional[int] = None) -> 'Excel':
        """
        定位到单元格
        :param row: 行号或单元格引用(如'A1')
        :param column: 列号，与row配合使用时指定
        :return: 当前实例
        """
        try:
            if column is None:
                self.cell_data = self.work_sheet[row]
            else:
                self.cell_data = self.work_sheet.cell(row=row, column=column)
        except Exception as e:
            logger.warning(f"定位单元格失败: {e}")
        return self
    
    def cell_value(self, data=None) -> Optional[Union[str, int, float, None]]:
        """
        读取或设置单元格值
        :param data: 要设置的值，None为读取，0为清除
        :return: 单元格的值
        """
        if data is not None:
            self.cell_data.value = data
            return self
        return self.cell_data.value if self.cell_data else None
    
    def cell_align_center(self) -> 'Excel':
        """设置单元格居中对齐"""
        if self.cell_data:
            self.cell_data.alignment = Alignment(horizontal='center', vertical='center')
        return self
    
    def cell_font_color(self, color: str) -> 'Excel':
        """
        设置字体颜色
        :param color: 颜色名称或十六进制色码
        """
        if self.cell_data:
            hex_color = self.COLOR_MAP.get(color.lower(), color)
            self.cell_data.font = Font(color=hex_color)
        return self
    
    def cell_bg_color(self, color: str) -> 'Excel':
        """
        设置背景颜色
        :param color: 颜色名称或十六进制色码
        """
        if self.cell_data:
            hex_color = self.COLOR_MAP.get(color.lower(), color)
            self.cell_data.fill = fill(hex_color)
        return self
    
    def cell_auto_column(self, length: Optional[int] = None, mode: str = 'loose') -> 'Excel':
        """
        自动调整列宽
        :param length: 内容长度，不传则从单元格值计算
        :param mode: 'loose'宽松模式或有缓冲，'tight'紧凑无缓冲
        :return: 当前实例
        """
        if not self.cell_data:
            return self
            
        cell_position = self.cell_data.coordinate
        column_name = get_column_name(cell_position)
        content_length = length if length is not None else len(str(self.cell_data.value) or '')
        
        # 更新最大长度缓存
        current_max = self._cell_max_len_dict.get(column_name, 0)
        new_max = max(current_max, content_length)
        self._cell_max_len_dict[column_name] = new_max
        
        # 计算宽度
        if mode == 'loose':
            width = (new_max + CELL_PADDING) * COLUMN_SCALE_FACTOR
        else:
            width = new_max
        
        self.work_sheet.column_dimensions[column_name].width = width
        return self
    
    def cell_add_image(
        self,
        image_path: str,
        size_w_h: List[int] = [128, 128],
        resize_rate: float = 0,
        anchor_cell: Optional[str] = None
    ) -> 'Excel':
        """
        在单元格添加图片
        :param image_path: 图片路径
        :param size_w_h: [宽度，高度] 像素
        :param resize_rate: 缩放比例，<=0则不缩放
        :param anchor_cell: 锚定单元格坐标，不传则使用当前选中单元格
        :return: 当前实例
        """
        if not self.cell_data and not anchor_cell:
            logger.error("未指定单元格位置")
            return self
        
        # 确定目标单元格
        target_cell = anchor_cell or (self.cell_data.coordinate if self.cell_data else 'A1')
        
        # 尺寸转换
        width_transform = Transform(size_w_h[0])
        height_transform = Transform(size_w_h[1])
        
        # 打开并处理图片
        try:
            if resize_rate > 0:
                new_width = int(width_transform.pixels * resize_rate)
                new_height = int(height_transform.pixels * resize_rate)
                resized_path = get_resize_image_path(image_path, new_width, new_height)
                self._temp_files.append(resized_path)
                xl_image = XLImage(Image.open(resized_path))
                xl_image.width = new_width
                xl_image.height = new_height
            else:
                xl_image = XLImage(Image.open(image_path))
                xl_image.width = width_transform.pixels
                xl_image.height = height_transform.pixels
            
            self.work_sheet.add_image(xl_image, target_cell)
            
            # 调整行高和列宽适应图片
            row_num = int(''.join(filter(str.isdigit, target_cell)))
            col_letter = ''.join(filter(str.isalpha, target_cell))
            
            self.work_sheet.row_dimensions[row_num].height = height_transform.points
            self.work_sheet.column_dimensions[col_letter].width = width_transform.points / 6
            
        except Exception as e:
            logger.error(f"添加图片失败: {e}")
            raise
        
        return self
    
    def save(self, name: str) -> str:
        """
        保存Excel文件
        :param name: 文件名(不含扩展名)
        :return: 保存的文件路径
        """
        output_path = f"{name}.xlsx"
        self.work_book.save(output_path)
        self.file_path = output_path
        logger.info(f"文件已保存: {output_path}")
        return output_path
    
    def close(self):
        """关闭工作簿并清理资源"""
        self._cleanup_temp_files()
        if self.work_book:
            self.work_book.close()
            self.work_book = None


if __name__ == '__main__':
    # 示例用法
    with Excel() as excel:
        excel.cell(1, 1).cell_value('Hello').cell_font_color('blue').cell_align_center()
        excel.cell(2, 1).cell_value('World').cell_bg_color('yellow')
        excel.cell_auto_column()
        excel.save('demo_output')