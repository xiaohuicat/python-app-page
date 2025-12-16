# 1. 导入语句分组，并使用绝对导入（如果可能）
import os
from functools import partial
from typing import Dict, List, Optional

# 假设 app_page 是一个可以被这样导入的包
from app_page import Page, Config, Param
from app_page.animation import RightClick_Menu
from app_page.utils import setAppStyle, select_image, assetsPath, encode

# 2. 将固定的样式和模板字符串定义为常量，并使用更清晰的命名
# 使用三引号和 f-string 提高可读性和可维护性
CSS_TAB_BUTTONS = """
.tab-btn {
  color: #666;
  border-radius: 15px;
  border: 1px solid #c0c0c0;
}
.tab-btn.active {
  color: #fff;
  background-color: #6666FF;
  border: 1px solid #6666FF;
}
"""

# 3. 将动态CSS生成逻辑封装成函数，而不是使用复杂的lambda
def get_card_style(item: Dict) -> str:
    """根据皮肤项信息生成卡片的CSS样式字符串。"""
    # 确保路径处理的健壮性
    bg_image_path = item.get('app_bg_image', '').replace('\\', '/')
    # 使用f-string格式化，更清晰
    return encode(f"""
.container {{
  border-radius: 12px;
  border-image: url('{bg_image_path}') stretch;
}}
""")

def get_status_style(current_id: str, item: Dict) -> str:
    """根据当前选中状态生成状态指示器的CSS样式字符串。"""
    bg_color = "red" if current_id == item["id"] else "transparent"
    return encode(f"""
border: 1px solid #fff;
border-radius: 9px;
background-color: {bg_color};
""")

# 4. HTML模板使用f-string，并将静态CSS内联进去
# 移除了不必要的 encode 调用，因为模板引擎可能会处理，或者在传递前已编码
TEMPLATE = f"""
<template>
  <div style="{encode(CSS_TAB_BUTTONS)}">
    <h-box align="AlignLeft" spacing="15">
      <button id="select-featured" class="tab-btn active" height="30" width="60" text="精选"/>
      <button id="select-all" class="tab-btn" height="30" width="60" text="全部"/>
    </h-box>
  </div>
  <div>
    <h-box margins="[0,8,0,15]">
      % for each in cardList:
        <button
          id="${{each['id']}}" 
          class="container" 
          height="160" 
          width="260" 
          style="${{getCardStyle(each)}}"
        >
          <v-box>
            <div></div>
            <div height="42">
              <h-box>
                <label text="${{encode(each['name'])}}"/>
                <div
                  id="status_${{each['id']}}"
                  width="18"
                  height="18"
                  style="${{getStatusStyle(current, each)}}"
                />
              </h-box>
            </div>
          </v-box>
        </button>
      % endfor
    </h-box>
  </div>
</template>
"""


class Skin(Page):  # 6. 类名更具描述性
    """皮肤选择页面。"""
    
    # 7. 将固定配置提取为类属性
    DEFAULT_THEME = Config().default_theme

    def __init__(self):
        super().__init__()
        self.template = TEMPLATE
        path = self.param.pathJoin('userPath', 'setting.json')
        self.setting = Param(path, self.DEFAULT_THEME)
        self.card_list: List[Dict] = []
        self.current_skin_id: str = self.DEFAULT_THEME['skinId']

    def setup(self):
        """设置页面上下文数据。"""
        # 从配置中加载数据
        self.card_list = self.setting.get("skinStyle", [])
        self.current_skin_id = self.setting.get("skinId", self.DEFAULT_THEME['skinId'])
        
        # 9. 将方法和数据打包成上下文，供模板使用
        return {
          'current': self.current_skin_id,
          'cardList': self.card_list,
          'encode': encode,
          'getCardStyle': get_card_style,
          'getStatusStyle': get_status_style,
        }

    def show(self, *args):
        """页面显示时的初始化工作（如绑定事件）。"""
        # 10. 优化事件注册：避免在循环中反复调用 self.getWidget
        # 如果框架允许，一次性获取所有卡片 widget 会更高效
        for index, card in enumerate(self.card_list):
            card_id = card['id']
            widget = self.getWidget(card_id)
            if not widget:
                continue # 跳过无效的widget
            
            # 添加右键菜单
            RightClick_Menu(widget, [
                {"name": "分享", "callback": partial(self.share_skin, index), "icon": assetsPath('menu', 'share.png')},
                {"name": "收藏", "callback": partial(self.love_skin, index), "icon": assetsPath('menu', 'love.png')},
                {"name": "更换壁纸", "callback": partial(self.change_image, index), "icon": assetsPath('menu', 'pictures.png')},
            ])
            # 注册点击事件
            self.register(card_id, 'clicked', partial(self.pick_skin, index))

    def pick_skin(self, index: int):
        """选择一个皮肤。"""
        new_skin_id = self.card_list[index]["id"]
        if self.current_skin_id == new_skin_id:
            return # 如果点击的是当前已选中的皮肤，则不做任何操作
        
        # 更新配置
        self.setting.set("skinId", new_skin_id)
        self.setting.save()
        
        # 应用新样式并刷新UI
        setAppStyle()
        self.playMedia('media', 'clicking-on.mp3')
        
        # 11. 简化刷新逻辑，setup已经包含了最新数据
        self.rerender(self.setup()) 
        # 注意：rerender 可能会重新创建所有 widget，因此可能需要重新调用 show 来绑定事件
        # 如果框架的 rerender 会自动触发 show，则可以省略下面这行
        self.show() 

    def change_image(self, index: int):
        """为指定皮肤更换背景图片。"""
        # 12. 提供更友好的默认路径和标题
        initial_dir = assetsPath('skin') or os.path.expanduser("~")
        output, _ = select_image(self.getParent(), initial_dir, title="请选择一张图片作为皮肤背景")
        if not output:
            return

        # 保存背景图片路径
        self.card_list[index]["app_bg_image"] = output
        self.setting.save()
        
        # 13. 仅当更换的是当前皮肤的图片时，才立即应用样式
        if self.card_list[index]["id"] == self.current_skin_id:
            setAppStyle()
        
        # 刷新UI以显示新的背景图
        self.rerender(self.setup())
        self.show()

    def love_skin(self, index: int):
        """收藏皮肤（模拟）。"""
        skin_name = self.card_list[index].get('name', '此皮肤')
        self.tips(f"已收藏 {skin_name}", "success")

    def share_skin(self, index: int):
        """分享皮肤（开发中）。"""
        self.tips("分享功能正在开发中，敬请期待...")