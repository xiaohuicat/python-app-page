# app_page_timer_bottle.py
import time
from datetime import datetime, timedelta
from app_page import Page, tryRun, updateStyle
from app_page.utils import assetsUrl
from PySide6.QtCore import QTimer, QObject
from PySide6.QtWidgets import QPushButton


# HTML模板
timer_template = """
<template>
    <div class="container">
        <v-box spacing="20">
            <div>
                <v-box spacing="30" align="AlignCenter" margins="[0,30,0,30]">
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
                    <div class="bottle-container" width="655" height="150" >
                        <h-box spacing="0" scroll="True" margins="[0,0,0,0]">
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
                    % endif:
                    
                    <!-- 统计信息展示区 -->
                    <div class="stats-container" height="120">
                        <v-box spacing="5">
                            <label
                                align="AlignCenter"
                                text="今日学习 ${stats_today['study']} 分钟, 休息 ${stats_today['rest']} 分钟" 
                                class="stat-line small"
                            />
                        </v-box>
                    </div>


                    <!-- 控制按钮 -->
                    <div>
                        <h-box spacing="30" align="AlignCenter">
                            <button
                                id="toggleModeBtn"
                                text="${toggleButtonText}"
                                class="btn mode-btn ${current_mode}"
                                width="150"
                            />
                            <button
                                id="taskDone"
                                text="完成任务"
                                class="btn mode-btn done"
                                width="150"
                            />
                        </h-box>
                    </div>
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


class TimerBottle(Page):
    STUDY_MODE = "study"
    REST_MODE = "rest"

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

        # --- 修改开始 ---
        # 计算今天的学习总时间（秒）
        today_study_seconds = stats["today"][self.STUDY_MODE]
        
        # 将秒转换为时:分:秒格式
        hours, remainder = divmod(int(today_study_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        self.isEmptyBottle = len(bottle_list) == 0

        return {
            "toggleButtonText": self.getToggleButtonText(),
            "bottle_list": bottle_list,
            "value_to_height": lambda v: int(109 * (28 + 0.72 * v) // 100) if isNum(v) else 0,
            # 将秒转换为分钟用于显示
            "stats_today": {k: round(v / 60) for k, v in stats["today"].items()},
            "stats_3day": {k: round(v / 60) for k, v in stats["3day"].items()},
            "stats_7day": {k: round(v / 60) for k, v in stats["7day"].items()},
            # 使用新计算的今天学习总时间
            "timer_text": timer_text,
            "current_mode": self.current_mode,
        }


    def loadHistory(self):
        """从本地存储加载历史记录"""
        stored_data = self.localStore.get("history", [])
        # 确保数据格式正确
        self.history = [item for item in stored_data if len(item) == 3 and isinstance(item[0], (int, float))]
        # 检查是否有未完成的会话
        last_entry = self.history[-1] if self.history else None
        if last_entry and last_entry[1] == 0: # 0 表示会话未结束
            # 如果上次是运行状态，恢复它
            if self.localStore.get("is_running", False):
                self.current_mode = last_entry[2]
                self.session_start_time = last_entry[0]
                self.is_running = True
            else: # 否则，将其标记为已结束
                last_entry[1] = last_entry[0] # 结束时间等于开始时间，表示无效或瞬间结束


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
        """根据总学习秒数生成水瓶列表"""
        total_study_hours = total_study_seconds / 3600
        bottle_list = []

        full_hours = int(total_study_hours)
        for _ in range(full_hours):
            bottle_list.append({"water_value": 100})

        remaining_hours = total_study_hours - full_hours
        if remaining_hours > 0:
            water_percent = int(remaining_hours * 100)
            if water_percent > 0: # 避免添加0水量的空瓶
                bottle_list.append({"water_value": water_percent})

        print(f"Total study hours: {total_study_hours}, Bottles generated: {len(bottle_list)}")
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

        # 如果加载时正在运行，则启动定时器
        if self.is_running:
            self.timer.start(1000)


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
            self.localStore.set("is_running", True)

        # 检查是否存在未完成的计时，如果结束，创建新计时
        last_entry = self.history[-1] if self.history else None
        if last_entry and last_entry[1] == 0: # 0 表示会话未结束
            last_entry[1] = time.time() # 结束当前计时
        # 开始新计时
        self.history.append([time.time(), 0, self.current_mode])
        self.localStore.set("history", self.history)

        # 更新UI
        toggleBtn: QPushButton = self.getWidget("toggleModeBtn")
        toggleBtn.setText(self.getToggleButtonText())
        toggleBtn.setProperty("class", f"btn mode-btn {self.current_mode}")
        updateStyle(toggleBtn)


    def onTimerTick(self):
        if self.getStatus() != "hide":
            # 重新渲染页面以更新计时器显示
            self.timer.stop()
            self.rerender(self.setup())
            self.show() 