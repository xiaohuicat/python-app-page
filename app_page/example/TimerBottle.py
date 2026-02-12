from app_page import Page, Param
from app_page.utils import assetsUrl
from PySide6.QtCore import QTimer, QObject
from datetime import timedelta

timer_template = """
<template>
    <div class="container">
        <v-box scroll="True" spacing="20">
            <div>
                <v-box spacing="30" align="AlignCenter">
                    <label id="timeDisplay" text="00:00" class="time-display" />
                    <div>
                        <h-box spacing="0" align="AlignCenter">
                            <div class="bottle"  height="128" width="128">
                                <v-box align="AlignBottom" spacing="0" margins="[0,0,0,0]">
                                    <div class="water" height="109" width="93" />
                                </v-box>
                            </div>
                            <div class="bottle"  height="128" width="128">
                                <v-box align="AlignBottom" spacing="0" margins="[0,0,0,0]">
                                    <div class="water" height="109" width="93" />
                                </v-box>
                            </div>
                            <div class="bottle"  height="128" width="128">
                                <v-box align="AlignBottom" spacing="0" margins="[0,0,0,0]">
                                    <div class="water" height="109" width="93" />
                                </v-box>
                            </div>
                            <div class="bottle"  height="128" width="128">
                                <v-box align="AlignBottom" spacing="0" margins="[0,0,0,0]">
                                    <div class="water" height="${water_value}" width="93" />
                                </v-box>
                            </div>
                        </h-box>
                    </div>
                    <div>
                        <h-box spacing="30" align="AlignCenter">
                            <button id="startPause" text="${startPauseText}" class="btn" width="120" />
                            <button id="reset" text="重置" class="btn reset" width="120" />
                        </h-box>
                    </div>
                </v-box>
            </div>
        </v-box>
    </div>
</template>
"""

timer_style = """
.container {
  border-radius: 12px;
  background-color: rgba(255, 255, 255, 0.6);
}
.time-display {
  font-size: 128px;
  font-weight: 800;
  font-family: 'Courier New', Courier, monospace;
  color: #e74c3c;
  background: #ffffff;
  padding: 30px 40px;
  border-radius: 30px;
  min-width: 320px;
  text-align: center;
}
.btn {
  font-size: 18px;
  padding: 12px;
  border-radius: 8px;
  background-color: #3498db;
  color: white;
  border: none;
}
.btn:hover {
  background-color: #2980b9;
}
.reset {
  background-color: #7f8c8d;
}
.reset:hover {
  background-color: #95a5a6;
}
.small {
  font-size: 14px;
  color: #7f8c8d;
}
.bottle {
  background-image: url("""+ assetsUrl('icon', 'bottle.png') +""");
}
.water {
  margin-left: 18px;
  margin-bottom: 18px;
  background-color: rgba(54, 156, 240, 0.6);
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
}
"""

def isNum(value):
  return isinstance(value, (int, float))


class TimerBottle(Page, QObject):  # 同时继承 Page 和 QObject
    def __init__(self):
        QObject.__init__(self)  # 先初始化 QObject
        super().__init__("timer-bottle")  # 用于 localStore 持久化的名字
        
        self.template = timer_template
        self.style = timer_style
        
        self.seconds = 0          # 已过去秒数
        self.is_running = False
        self.target_seconds = 0   # 目标秒数（0 = 不限时）

    def setup(self) -> dict:
        self.onGlobalDestroy(self.saveGlobal)
        # 获取或创建计时器对象
        self.timer = self.getTimer()
        self.seconds = self.getGlobal("seconds", self.localStore.get("seconds", 0))
        self.is_running = self.localStore.get("is_running", False)
        per = 28 + 0.72 * 30
        return {
            "water_value": int(109 * per // 100),  # 水位高度（根据百分比计算）
            "startPauseText": "开始",
        }

    def getTimer(self):
        # 获取或创建计时器对象
        timer = self.getGlobal("timer", None)
        if not timer:
            timer = QTimer()
            self.setGlobal("timer", timer)
        else:
            timer.timeout.disconnect()
        timer.timeout.connect(self.updateTime)
        return timer

    def show(self, *args):      
        # 显示时间
        self.updateDisplay()
        
        # 绑定事件
        self.register("startPause", "clicked", self.toggleTimer)
        self.register("reset", "clicked", self.resetTimer)
        
        # 如果上次是运行状态，则继续
        if self.is_running:
            self.startTimer()
            self.getWidget("startPause").setText("暂停")
        else:
            self.getWidget("startPause").setText("开始" if self.seconds == 0 else "继续")

    def toggleTimer(self):
        if self.is_running:
            self.pauseTimer()
        else:
            self.startTimer()

    def startTimer(self):
        try:
            target_str = self.getWidget("targetSec").text().strip()
            self.target_seconds = int(target_str) if target_str else 0
        except:
            self.target_seconds = 0

        self.timer.start(1000)           # 每1000ms触发一次
        self.is_running = True
        self.getWidget("startPause").setText("暂停")
        self.localStore.set("is_running", True)

    def pauseTimer(self):
        self.timer.stop()
        self.is_running = False
        self.getWidget("startPause").setText("继续")
        self.localStore.set("is_running", False)

    def resetTimer(self):
        self.timer.stop()
        self.seconds = 0
        self.is_running = False
        self.updateDisplay()
        self.getWidget("startPause").setText("开始")
        self.localStore.set("seconds", 0)
        self.localStore.set("is_running", False)

    def updateTime(self):
        self.seconds += 1
        self.setGlobal("seconds", self.seconds)
        if self.getStatus() == "hide":
            print(f"计时中... 已用时 {self.seconds} 秒")
            return
        
        self.updateDisplay()
        
        # 到达目标时间提醒（可选）
        if self.target_seconds > 0 and self.seconds >= self.target_seconds:
            self.timer.stop()
            self.is_running = False
            self.getWidget("startPause").setText("开始")
            self.tips(f"计时结束！已用时 {self.seconds} 秒", "success")

    def updateDisplay(self):
        t = str(timedelta(seconds=self.seconds))[-5:]   # 只取 mm:ss 部分
        if len(t) == 4:
            t = "0" + t
        self.getWidget("timeDisplay").setText(t)


    def saveGlobal(self):
        # 在页面关闭或切换时保存状态
        localStore = Param(self.getSoftwarePath("userPath", f"pages/{self.name}/config.json"), {})
        localStore.set("seconds", self.getGlobal("seconds", self.seconds))
        localStore.save()