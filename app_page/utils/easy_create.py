from .common import assetsUrl, encode

def empty_container_qss(opacity=0.8):
    """生成空容器QSS样式
    
    Args:
        opacity (float): 背景透明度，范围0-1
    
    Returns:
        str: QSS样式字符串
    """
    return f'''
        .empty-container {{
            background-color: rgba(255, 255, 255, {opacity});
            border-radius: 10px;
        }}
        .empty-image {{
            border-image: url({assetsUrl('image', 'empty.png')});
        }}
        .empty-text {{
            color: #8a8e99;
            font-size: 16px;
        }}
    '''

def empty_container_xml(message="暂无数据"):
    """生成空容器XML结构
    
    Args:
        message (str): 提示消息
    
    Returns:
        str: XML结构字符串
    """
    encoded_msg = html.escape(str(message)) if hasattr(html, 'escape') else encode(message)
    return f'''
    <div class="empty-container">
        <v-box align="AlignCenter" height="400">
            <div>
                <v-box align="AlignCenter">
                    <label width="64" height="64" class="empty-image" />
                </v-box>
            </div>
            <label text="{encoded_msg}" align="AlignCenter" class="empty-text" />
        </v-box>
    </div>'''

# 补充导入
import html