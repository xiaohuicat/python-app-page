from .common import assetsUrl, encode

def empty_container_qss(opacity=0.8):
    return """
        .empty-container {
            background-color: rgba(255, 255, 255, """ + str(opacity) + """);
            border-radius: 10px;
        }
        .empty-image {
            border-image: url('""" + assetsUrl('image', 'empty.png') + """');
        }
        .empty-text {
            color: #8a8e99;
            font-size: 16px;
        }
        """

def empty_container_xml(message="暂无数据"):
    return f'''
        <div class="empty-container">
            <v-box align="AlignCenter" height="400">
                <div>
                    <v-box align="AlignCenter">
                        <label width="64" height="64" class="empty-image" />
                    </v-box>
                </div>
                <label text="{encode(message)}" align="AlignCenter" class="empty-text" />
            </v-box>
        </div>'''