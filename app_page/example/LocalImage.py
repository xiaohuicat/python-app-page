import os
from pathlib import Path
from app_page import Page
from app_page.utils import (encode, s2t, assetsUrl, get_file_md5, create_folder, 
                            cut_image, open_folder, copy_image, delete_file, empty_container_qss, empty_container_xml)
from PySide6.QtWidgets import QWidget
from ..utils.date_time import timestamp_to_str
from ..components import ShowImage


# 页面模板
TEMPLATE = """
<template>
    <div class="container">
        <v-box spacing="10" align="AlignTop">
            <div height="40">
                <h-box margins="[0,0,0,0]">
                    <label class="title" text="${title}" />
                    <button class="primary-button" id="openFolder" text="打开" width="60" height="26" />
                </h-box>
            </div>
            <div>
                <v-box scroll="True" margins="[0,0,0,0]">
                % if len(images) > 0:
                    % for index, img in enumerate(images):
                        <div>
                            <h-box spacing="10" margins="[0,10,0,0]">
                                <button
                                    width="180"
                                    height="120"
                                    index="${index}"
                                    event-filter="open"
                                    style="${getImageStyle(img)}"
                                />
                                <div>
                                    <v-box spacing="5">
                                        <div>
                                            <h-box margins="[0,0,0,0]">
                                                <label text="${encode(img['name'])}" class="image-name" />
                                                <button index="${index}" event-filter="copy" class="copy-button" width="24" height="24" />
                                                <button index="${index}" event-filter="love" class="love-button" width="24" height="24" />
                                                <button index="${index}" event-filter="delete" class="delete-button" width="24" height="24" />
                                            </h-box>
                                        </div>
                                        <label class="image-desc" text="大小: ${img['size']}" />
                                        <label class="image-desc" text="修改时间: ${img['mtime']}" />
                                    </v-box>
                                </div>
                            </h-box>
                        </div>
                    % endfor
                % else:
                    ${empty_container_xml('没有找到图片' if not isLoading else '正在加载...')}
                % endif
                </v-box>
            </div>
        </v-box>
    </div>
</template>
"""

# 页面样式
STYLE = """
.container {
    background-color: rgba(255,255,255,0.6);
    border-radius: 10px;
}
.title {
    background-color: transparent;
    font-size: 22px;
    font-weight: bold;
}
.primary-button {
    font-size: 14px;
    border-radius: 8px;
    background-color: #409EFF;
    color: #ffffff;
}
.copy-button {
    border-image: url('"""+assetsUrl('icon', 'local-image', 'copy.png')+"""');
}
.delete-button {
    border-image: url('"""+assetsUrl('icon', 'local-image', 'delete.png')+"""');
}
.love-button {
    border-image: url('"""+assetsUrl('icon', 'local-image', 'love.png')+"""');
}
.love-full-button {
    border-image: url('"""+assetsUrl('icon', 'local-image', 'love_full.png')+"""');
}
.image-name {
    color: #333;
    font-weight: bold;
    font-size: 14px;
}
.image-desc {
    color: #8a8e99;
    font-size: 12px;
}

""" + empty_container_qss()

# 支持的图片扩展名
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff', '.tif', '.ico')
# 缩略图尺寸
THUMBNAIL_SIZE = (180, 120)
# 页面标题常量
PAGE_TITLE_DEFAULT = "我的图片"
# 临时目录相对路径
THUMBNAIL_REL_PATH = ("tempPath", "images", "local-images")


class LocalImage(Page):
    """
    本地图片管理页面类
    功能：
    1. 读取用户图片目录下的所有图片文件
    2. 生成并展示图片缩略图
    3. 支持打开、复制图片操作
    4. 支持打开图片所在目录
    """
    
    def __init__(self):
        super().__init__()
        self.image_dir: Path = Path(os.path.expanduser("~/Pictures"))
        self.template = TEMPLATE
        self.style = STYLE
        self.image_viewer = None
        self.is_recursion = False
        self._md5_cache: dict[str, str] = {}  # MD5缓存，避免重复计算

    def setup(self) -> dict:
        """
        页面初始化数据
        
        Returns:
            dict: 模板渲染所需的上下文数据
        """
        images = self.pageParam.get('images', [])
        title = f"{PAGE_TITLE_DEFAULT} ({len(images)})" if images else PAGE_TITLE_DEFAULT
        
        return {
            's2t': s2t,
            'encode': encode,
            'assetsUrl': assetsUrl,
            'title': title,
            'images': images,
            'isLoading': self.pageParam.get('isLoading', False),
            'getImageStyle': self._get_image_style,  # 替换lambda为独立方法，更易维护
            'empty_container_xml': empty_container_xml,
        }

    def _get_image_style(self, img: dict) -> str:
        """
        生成图片按钮的样式字符串
        
        Args:
            img: 图片信息字典
            
        Returns:
            编码后的样式字符串
        """
        style_str = f"border-radius:8px;border-image:url('{img['small-path']}');"
        return encode(style_str)

    def show(self, *args):
        """页面显示时的初始化操作"""
        # 是否加载图片
        if not self.pageParam.get('load-finished', False):
            self.load_images()
            return
        
        # 注册打开文件夹事件
        self.register('openFolder', 'clicked', lambda *args: self._open_image_folder())
        # 注册点击代理事件
        self.regist_filter(self._click_filter)

    def hide(self, *args):
        """页面隐藏时清理资源"""
        self._close_image_viewer()
        # 清空MD5缓存
        self._md5_cache.clear()

    def load_images(self):
        """加载本地图片（对外接口）"""
        print("加载本地图片...")
        self.pageParam.set('isLoading', True)
        self.rerender(self.setup())
        # 异步加载图片信息
        self.async_run(self._load_image_info, self._load_callback)

    def open_image(self, image_path: str):
        """
        打开指定路径的图片
        
        Args:
            image_path: 图片文件的绝对路径
        """
        try:
            self._close_image_viewer()
            self.image_viewer = ShowImage(
                page=self,
                savePath=str(self.image_dir),
                currentPath=image_path
            )
            self.image_viewer.show_image()
            self.image_viewer.show()
        except Exception as e:
            self.tips(f"打开图片失败: {str(e)}", 'error')

    def copy_image(self, image_path: str):
        """
        复制指定路径的图片到剪贴板
        
        Args:
            image_path: 图片文件的绝对路径
        """
        try:
            print(f'复制图片：{image_path}')
            copy_image(image_path)
            self.tips('图片已复制', 'success')
        except Exception as e:
            self.tips(f"复制图片失败: {str(e)}", 'error')

    def delete_image(self, image_path: str):
        def run():
            try:
                delete_file(image_path)
                self.async_run(self._load_image_info, self._load_callback)
            except Exception as error:
                self.tips(str(error), 'fail')
        self.tipsBox('删除图片', '是否将该图片永久删除？', '删除后不可恢复', confirm=run)

    def _close_image_viewer(self):
        """关闭图片查看器并释放资源"""
        if self.image_viewer:
            try:
                self.image_viewer.close()
                self.image_viewer.destroy()
            except Exception as e:
                print(f"关闭图片查看器时出错: {e}")
            finally:
                self.image_viewer = None

    def _click_filter(self, widget:QWidget):
        filter_type = widget.property('event-filter')
        index = int(widget.property('index'))
        images = self.pageParam.get('images', [])
        if filter_type == 'open':
            self.open_image(images[index]['path'])
        elif filter_type == 'copy':
            self.copy_image(images[index]['path'])
        elif filter_type == 'love':
            self.tips('正在开发')
        elif filter_type == 'delete':
            self.delete_image(images[index]['path'])

    def _open_image_folder(self):
        """打开图片所在目录（封装为独立方法）"""
        try:
            print(f'打开图片目录：{self.image_dir}')
            open_folder(str(self.image_dir))
        except Exception as e:
            self.tips(f"打开文件夹失败: {str(e)}", 'error')

    def _load_image_info(self) -> list[dict]:
        """
        异步加载图片信息（内部方法）
        包含：生成缩略图、获取文件元信息等
        可控：通过 self.is_recursion 控制是否递归遍历子文件夹
        
        Returns:
            包含所有图片信息的列表（按修改时间降序排列）
        """
        images = []
        
        # 检查目录是否存在
        if not self.image_dir.exists():
            return images
        
        # 创建缩略图存放目录
        thumbnail_dir = self.getSoftwarePath(*THUMBNAIL_REL_PATH)
        create_folder(thumbnail_dir)
        
        # 根据 is_recursion 选择遍历模式
        image_files = []
        if self.is_recursion:
            # 开启递归：遍历当前目录及所有子目录
            image_patterns = [f"**/*{ext}" for ext in IMAGE_EXTENSIONS]
            for pattern in image_patterns:
                image_files.extend(self.image_dir.glob(pattern))
        else:
            # 关闭递归：仅遍历当前目录
            for filename in os.listdir(self.image_dir):
                file_path = self.image_dir / filename
                # 过滤非图片文件和目录
                if (file_path.is_file() and 
                    filename.lower().endswith(IMAGE_EXTENSIONS)):
                    image_files.append(file_path)
        
        # 遍历所有匹配的图片文件（全局索引）
        for index, file_path in enumerate(image_files, 1):
            try:
                # 双重校验：确保是文件（防止异常情况）
                if not file_path.is_file():
                    continue
                
                filename = file_path.name
                file_path_str = str(file_path)
                
                # 获取文件MD5（使用缓存）
                if file_path_str not in self._md5_cache:
                    self._md5_cache[file_path_str] = get_file_md5(file_path_str)
                md5_name = self._md5_cache[file_path_str]
                
                # 生成缩略图路径
                file_ext = file_path.suffix.lower()
                thumbnail_filename = f"{md5_name}{file_ext}"
                thumbnail_path = Path(thumbnail_dir) / thumbnail_filename
                
                # 生成缩略图（仅当不存在时）
                if not thumbnail_path.exists():
                    cut_image(
                        str(file_path),
                        str(thumbnail_path),
                        THUMBNAIL_SIZE,
                        'out'
                    )
                
                # 获取文件元信息
                stat = file_path.stat()
                file_size = self._format_file_size(stat.st_size)
                modify_time = timestamp_to_str(stat.st_mtime * 1000)
                st_mtime = stat.st_mtime

                # 构建图片信息字典
                image_info = {
                    'id': f'image-{index}',
                    'name': filename,
                    'path': file_path_str.replace('\\', '/'),
                    'small-path': str(thumbnail_path).replace('\\', '/'),
                    'size': file_size,
                    'mtime': modify_time,
                    'st_mtime': st_mtime,
                }
                # 仅当递归开启时，添加相对路径字段
                if self.is_recursion:
                    image_info['relative_path'] = str(file_path.relative_to(self.image_dir)).replace('\\', '/')
                
                images.append(image_info)
                
            except PermissionError:
                print(f"无权限访问文件: {file_path}")
                continue
            except Exception as e:
                print(f"处理图片失败: {file_path} - {e}")
                continue
        
        # 按修改时间降序排序（最新的在前）
        return sorted(images, key=lambda x: x['st_mtime'], reverse=True)

    def _load_callback(self, result: list[dict]):
        """
        图片加载完成后的回调函数
        
        Args:
            result: 加载到的图片信息列表
        """
        self.pageParam.set('isLoading', False)
        self.pageParam.set('images', result)
        self.pageParam.set('load-finished', True)
        self.rerender(self.setup())
        self.show()

    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """
        格式化文件大小为人类可读的格式
        
        Args:
            size_bytes: 以字节为单位的文件大小
            
        Returns:
            格式化后的大小字符串（B/KB/MB）
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"