# app_page_timer_bottle.py
import time
from datetime import datetime, timedelta
from app_page import Page
from app_page.utils import assetsUrl, d2t, tryRun, updateStyle
from app_page.animation import smoothScroll
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QPushButton


# HTML模板
timer_template = """
<template>
    <div class="container" size-policy="True">
        <v-box spacing="20">
            <div>
                <v-box spacing="20" align="AlignCenter" margins="[0,30,0,30]">
                    <!-- 时间显示 -->
                    <label
                        id="timeDisplay"
                        class="time-display"
                        text="${timer_text}"
                        align="AlignCenter"
                        margins="[30,40,30,40]"
                    />

                    <!-- 水瓶展示区 -->
                    % if len(bottle_list) > 0:
                    <div id="bottle-container" class="bottle-container" width="655" height="150" >
                        <h-box spacing="0" scroll="${scroll_option}" margins="[0,0,0,0]">
                            <div>
                                <h-box spacing="0" align="AlignCenter" margins="[0,0,0,0]">
                                    % for item in bottle_list:
                                        <div class="bottle"  height="128" width="128">
                                            <v-box align="AlignBottom" spacing="0" margins="[0,0,0,0]">
                                                <div
                                                    class="water"
                                                    height="${value_to_height(item['water_value'])}"
                                                    width="93"
                                                />
                                            </v-box>
                                        </div>
                                    % endfor
                                </h-box>
                            </div>
                        </h-box>
                    </div>
                    % endif
                    
                    <!-- 统计信息展示区 -->
                    <div class="stats-container" height="80">
                        <v-box spacing="5">
                            <label
                                align="AlignCenter"
                                text="${stats_text}"
                                class="stat-line small"
                            />
                        </v-box>
                    </div>


                    <!-- 控制按钮 -->
                    % if is_running or len(bottle_list) == 0:
                    <div>
                        <h-box spacing="30" align="AlignCenter">
                            <button
                                id="toggleModeBtn"
                                text="${toggleButtonText}"
                                class="btn mode-btn ${current_mode}"
                                width="150"
                            />
                            <button
                                id="taskDoneBtn"
                                text="完成任务"
                                class="btn mode-btn done"
                                width="150"
                            />
                        </h-box>
                    </div>
                    % endif
                </v-box>
            </div>
        </v-box>
    </div>
</template>
"""


# CSS样式
timer_style = """
.container {
    border-radius: 12px;
    background-color: rgba(255, 255, 255, 0.6);
    padding: 20px;
}
.mode-label {
    font-size: 24px;
    color: #2c3e50;
    font-weight: bold;
}
.time-display {
    font-size: 128px;
    font-weight: bold;
    font-family: 'Courier New', Courier, monospace;
    color: #e74c3c;
    border-radius: 36px;
    background: #ffffff;
}
.bottle-container {
    margin-top: 10px;
    margin-bottom: 10px;
}
.stats-container {
    border-radius: 8px;
}
.stat-line {
    text-align: left;
}
.small {
    font-size: 14px;
    color: #7f8c8d;
}
.btn {
    font-size: 18px;
    padding: 12px;
    border-radius: 14px;
    color: white;
    border: none;
}
.btn:hover {
    opacity: 0.9;
}
.mode-btn {
    background-color: #000000; /* 默认为黑色 */
}
.mode-btn.study {
    background-color: #e67e22; /* 休息模式橙色 */
}
.mode-btn.rest {
    background-color: #27ae60; /* 学习模式绿色 */
}
.bottle {
    background-image: url('""" + assetsUrl('icon', 'bottle.png') + """');
    background-repeat: no-repeat;
    background-position: center;
}
.water {
    margin-left: 18px;
    margin-bottom: 18px;
    background-color: rgba(52, 152, 219, 0.7); /* 使用更鲜艳的蓝色 */
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}
"""


def isNum(value):
    return isinstance(value, (int, float))


def get_date(day=0):
    dt = datetime.now()
    if day != 0:
        dt = dt + timedelta(days=day)
    return dt.strftime("%Y-%m-%d")


class TimerBottle(Page):
    STUDY_MODE = "study"
    REST_MODE = "rest"
    TODAY_HISTORY = f"history/{get_date()}"

    def __init__(self):
        super().__init__("timer-bottle")
        self.template = timer_template
        self.style = timer_style
        
        self.current_mode = None  # 'study' or 'rest'. None means initial state.
        self.session_start_time = None
        self.is_running = False
        self.history = []
        self.timer = None


    def setup(self) -> dict:
        if not self.timer:
            self.timer = self.getTimer()

        # 加载历史数据
        self.loadHistory()

        # 计算统计数据和水瓶列表
        stats = self.calculateStats()
        bottle_list, total_study_hours = self.generateBottles(stats[self.STUDY_MODE]["total_seconds"])

        # 计算今天的学习总时间（秒）
        today_study_seconds = stats["today"][self.STUDY_MODE]
        
        # 将秒转换为时:分:秒格式
        hours, remainder = divmod(int(today_study_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        self.isEmptyBottle = len(bottle_list) == 0

        stats_today = {k: round(v / 60, 2) for k, v in stats["today"].items()}
        stats_text = f'今日学习 {stats_today['study']} 分钟, 休息 {stats_today['rest']} 分钟'

        return {
            "toggleButtonText": self.getToggleButtonText(),
            "bottle_list": bottle_list,
            "value_to_height": lambda v: int(109 * (28 + 0.72 * v) // 100) if isNum(v) else 0,
            "stats_text": stats_text,
            "timer_text": timer_text,
            "current_mode": self.current_mode,
            "is_running": self.is_running,
            "scroll_option": d2t({"id": "bottle-scroll-area"}),
        }


    def loadHistory(self):
        """从本地存储加载历史记录"""
        stored_data = self.localStore.get(self.TODAY_HISTORY, [])
        # 确保数据格式正确
        self.history = [item for item in stored_data if len(item) == 3 and isinstance(item[0], (int, float))]
        # 检查是否有未完成的会话
        last_entry = self.getCurrentHistory()
        if last_entry:
            self.current_mode = last_entry[2]
            self.session_start_time = last_entry[0]
            self.is_running = True


    def calculateStats(self):
        """计算今日、近3天、近7天的学习和休息时长"""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        three_days_ago_start = (now - timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        seven_days_ago_start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

        stats = {
            "today": {self.STUDY_MODE: 0, self.REST_MODE: 0},
            "3day": {self.STUDY_MODE: 0, self.REST_MODE: 0},
            "7day": {self.STUDY_MODE: 0, self.REST_MODE: 0},
            self.STUDY_MODE: {"total_seconds": 0}, # 用于生成水瓶
            self.REST_MODE: {"total_seconds": 0}
        }

        for start_ts, end_ts, mode in self.history:
            # 跳过未完成的会话（理论上这里不应该有，因为loadHistory已处理）
            if end_ts == 0:
                continue
            duration = end_ts - start_ts
            
            # 总时长统计
            stats[mode]["total_seconds"] += duration

            # 时间段统计
            if start_ts >= today_start:
                stats["today"][mode] += duration
            if start_ts >= three_days_ago_start:
                stats["3day"][mode] += duration
            if start_ts >= seven_days_ago_start:
                stats["7day"][mode] += duration

        # 如果当前会话正在运行，需要加上当前持续时间
        if self.is_running and self.session_start_time is not None:
            current_duration = time.time() - self.session_start_time
            stats[self.current_mode]["total_seconds"] += current_duration
            now_ts = now.timestamp()
            if now_ts >= today_start:
                stats["today"][self.current_mode] += current_duration
            if now_ts >= three_days_ago_start:
                stats["3day"][self.current_mode] += current_duration
            if now_ts >= seven_days_ago_start:
                stats["7day"][self.current_mode] += current_duration

        return stats


    def generateBottles(self, total_study_seconds):
        """根据总学习秒数生成水瓶列表（至少生成一个瓶子）"""
        total_study_hours = total_study_seconds / 3600
        bottle_list = []

        full_hours = int(total_study_hours)
        # 先添加完整小时对应的满水瓶
        for _ in range(full_hours):
            bottle_list.append({"water_value": 100})

        remaining_hours = total_study_hours - full_hours
        # 计算剩余小时对应的水量百分比
        water_percent = int(remaining_hours * 100)
        
        # 核心修复：如果没有完整小时，或者有剩余水量，都要保证至少有一个瓶子
        if total_study_seconds > 0:
            bottle_list.append({"water_value": water_percent if water_percent > 0 else 1})

        return bottle_list, total_study_hours


    def getTimer(self):
        timer = self.getGlobal("timer", None)
        if not timer:
            timer = QTimer()
            self.setGlobal("timer", timer)
        else:
            tryRun(lambda: timer.timeout.disconnect())
        timer.timeout.connect(self.onTimerTick)
        return timer


    def getToggleButtonText(self):
        """根据当前状态获取按钮文本"""
        if self.current_mode != self.STUDY_MODE:
            return "开始学习" if self.isEmptyBottle else "继续学习"
        else:
            return "暂停学习"


    def show(self, *args):
        self.register("toggleModeBtn", "clicked", self.onToggleModeClicked)
        self.register("taskDoneBtn", "clicked", self.onTaskDoneClicked)
        if self.is_running:
            self.timer.start(1000)
        self.setTimeout(lambda *args: smoothScroll(self.getWidget('bottle-scroll-area'), 'horizontal'), 0.1)


    def onToggleModeClicked(self):
        """
        核心逻辑修改：
        - 如果当前没有任何模式在运行 (self.current_mode is None)，则默认开始学习。
        - 如果当前模式暂停了 (self.is_running is False)，则继续该模式。
        - 如果当前模式正在运行 (self.is_running is True)，则暂停该模式。
        """
        if self.current_mode is None:
            self.current_mode = self.REST_MODE
        self.current_mode = self.STUDY_MODE if self.current_mode == self.REST_MODE else self.REST_MODE
        
        if not self.is_running:
            self.is_running = True

        # 检查是否存在未完成的计时，如果结束，创建新计时
        last_entry = self.getCurrentHistory()
        if last_entry:
            last_entry[1] = time.time()
        # 开始新计时
        self.history.append([time.time(), 0, self.current_mode])
        self.localStore.set(self.TODAY_HISTORY, self.history)

        # 更新UI
        toggleBtn: QPushButton = self.getWidget("toggleModeBtn")
        toggleBtn.setText(self.getToggleButtonText())
        toggleBtn.setProperty("class", f"btn mode-btn {self.current_mode}")
        updateStyle(toggleBtn)

        # 是否开启定时器
        if self.is_running:
            self.timer.start(1000)


    def onTimerTick(self):
        if self.getStatus() != "hide":
            self.rerender_page()


    def onTaskDoneClicked(self):
        def confirm():
            last_entry = self.getCurrentHistory()
            if last_entry:
                last_entry[1] = time.time()
            self.localStore.set(self.TODAY_HISTORY, self.history)
            self.is_running = False
            self.rerender_page()
        self.tipsBox('确认', '确认当日任务已完成', '完成后今日无法操作', confirm=confirm)


    def rerender_page(self):
        self.timer.stop()
        self.rerender(self.setup())
        self.show()


    def getCurrentHistory(self):
        last_entry = self.history[-1] if self.history else None
        if last_entry and last_entry[1] == 0:
            return last_entry
        else:
            return None