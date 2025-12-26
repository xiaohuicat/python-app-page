import os
from functools import partial
from typing import Dict, List
from PySide6.QtWidgets import QSlider, QLabel
from PySide6.QtCore import Qt
from app_page import Page, Config, Param
from app_page.animation import RightClick_Menu
from app_page.utils import clear_folder, setAppStyle, select_image, assetsPath, encode

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
            <div />
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
  <div>
    <h-box align="AlignLeft" spacing="15">
      <label text="模糊半径"/>
      <QSlider id="slider" height="32" />
      <label id="radius" text="100" width="40" />
      <button id="comfirm" text="确定" width="60" height="25" style="background-color:#f0f0f0;border-radius:6px;"/>
    </h-box>
  </div>
</template>
"""


class Skin(Page):
    """皮肤选择页面。"""
    DEFAULT_THEME = Config().default_theme
    def __init__(self):
        super().__init__()
        self.template = TEMPLATE
        self.current_radius = 0
        self.setting = Param(self.getSoftwarePath('userPath', 'setting.json'), self.DEFAULT_THEME)
        self.card_list: List[Dict] = []
        self.current_skin_id: str = self.DEFAULT_THEME['skinId']

    def setup(self):
        """设置页面上下文数据。"""
        self.card_list = self.setting.get("skinStyle", [])
        self.current_skin_id = self.setting.get("skinId", self.DEFAULT_THEME['skinId'])
        
        return {
          'current': self.current_skin_id,
          'cardList': self.card_list,
          'encode': encode,
          'getCardStyle': self.get_card_style,
          'getStatusStyle': self.get_status_style,
        }

    def show(self, *args):
        """页面显示时的初始化工作（如绑定事件）。"""
        for index, card in enumerate(self.card_list):
            card_id = card['id']
            widget = self.getWidget(card_id)
            if not widget:
                continue
            
            # 添加右键菜单
            RightClick_Menu(widget, [
                {"name": "分享", "callback": partial(self.share_skin, index), "icon": assetsPath('menu', 'share.png')},
                {"name": "收藏", "callback": partial(self.love_skin, index), "icon": assetsPath('menu', 'love.png')},
                {"name": "更换壁纸", "callback": partial(self.change_image, index), "icon": assetsPath('menu', 'pictures.png')},
            ])
            # 注册点击事件
            self.register(card_id, 'clicked', partial(self.pick_skin, index))
        
        radius_value = self.setting.get('radius', 10)
        slider:QSlider = self.getWidget('slider')
        radius:QLabel = self.getWidget('radius')
        def comfirm():
          clear_folder(self.getSoftwarePath('tempPath', 'blur_images'), False, False)
          self.setting.set('radius', self.current_radius)
          radius.setStyleSheet('color:blue;')
          self.refreshPage()
          setAppStyle()
        def changeRadius(value):
          self.current_radius = value
          radius.setText(str(value))
          radius.setStyleSheet('color:#333;')
        slider.valueChanged.connect(changeRadius)
        slider.setOrientation(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(radius_value)
        radius.setText(str(radius_value))
        radius.setStyleSheet('color:blue;')
        self.register('comfirm', 'clicked', comfirm)
    
    def hide(self, *args):
        super().hide()
        self.setting.save()

    def pick_skin(self, index: int):
        """选择一个皮肤。"""
        new_skin_id = self.card_list[index]["id"]
        if self.current_skin_id == new_skin_id:
            return
        
        self.setting.set("skinId", new_skin_id)
        self.setting.save()
        
        setAppStyle()
        self.playMedia('media', 'clicking-on.mp3')

        self.refreshPage()

    def change_image(self, index: int):
        """为指定皮肤更换背景图片。"""
        initial_dir = assetsPath('skin') or os.path.expanduser("~")
        output, _ = select_image(self.getParent(), initial_dir, title="请选择一张图片作为皮肤背景")
        if not output:
            return

        self.card_list[index]["app_bg_image"] = output
        self.setting.save()
        
        if self.card_list[index]["id"] == self.current_skin_id:
          setAppStyle()
        
        self.rerender(self.setup())
        self.show()

    def love_skin(self, index: int):
        """收藏皮肤（模拟）。"""
        skin_name = self.card_list[index].get('name', '此皮肤')
        self.tips(f"已收藏 {skin_name}", "success")

    def share_skin(self, index: int):
        """分享皮肤（开发中）。"""
        self.tips("分享功能正在开发中，敬请期待...")

    def get_card_style(self, item: Dict) -> str:
        """根据皮肤项信息生成卡片的CSS样式字符串。"""
        bg_image_path = item.get('app_bg_image', '').replace('\\', '/')
        bg_image_path = self.getBlurImage(bg_image_path, self.setting.get('radius', 10))
        return encode(f"""
          .container {{
            border-radius: 12px;
            border-image: url('{bg_image_path}') stretch;
          }}
          """)

    def get_status_style(self, current_id: str, item: Dict) -> str:
        """根据当前选中状态生成状态指示器的CSS样式字符串。"""
        bg_color = "red" if current_id == item["id"] else "transparent"
        return encode(f"""
          border: 1px solid #fff;
          border-radius: 9px;
          background-color: {bg_color};
        """)
    

    def refreshPage(self):
        self.setting.save()
        self.rerender(self.setup())
        self.show()