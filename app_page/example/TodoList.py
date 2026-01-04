from datetime import datetime, timedelta
from PySide6.QtWidgets import QWidget
from app_page import Page
from app_page.utils import encode, s2t, assetsUrl
from nanoid import generate


template = """
<template>
    <div class="container">
        <v-box spacing="15" align="AlignTop" margins="[0,0,0,0]">
            <!-- 标题和添加按钮 -->
            <div height="50">
                <h-box>
                    <label text="${title}" class="title" />
                    <button id="addTask" text="添加任务" width="100" height="30" class="text-button" />
                </h-box>
            </div>

            <!-- 任务列表 -->
            <div>
                <v-box scroll="True">
                % if len(tasks) > 0:
                    <div>
                        <v-box align="AlignTop" margins="[0,0,0,0]" spacing="10">
                        % for task in tasks:
                            <div class="card ${'done' if task['done'] else 'todo'}" height="75">
                                <h-box spacing="15" margins="[10,0,10,0]" >
                                    <!-- 完成复选框 -->
                                    <button
                                        id="${task['id']}"
                                        width="30"
                                        height="30"
                                        event-filter="check-box"
                                        class="${'check-done' if task['done'] else 'check-todo'}"
                                    />

                                    <!-- 任务内容 -->
                                    <div>
                                      <v-box>
                                          <label text="${encode(task['content'])}" class="${'task-text-done' if task['done'] else 'task-text'}"/>
                                          <label text="${encode(task['due_str'])}" class="due-text" style="color:${task['due_color']};" />
                                      </v-box>
                                    </div>

                                    <!-- 删除按钮 -->
                                    <button
                                        id="${task['id']}"
                                        width="24"
                                        height="24"
                                        event-filter="delete-task"
                                        class="delete-button"
                                    />
                                </h-box>
                            </div>
                        % endfor
                        </v-box>
                    </div>
                % else:
                    <div class="empty-container">
                        <v-box align="AlignCenter" height="400">
                            <label width="400" height="300" class="empty-image" />
                            <label text="暂无任务，快去添加一个吧~" align="AlignCenter" class="empty-text" />
                        </v-box>
                    </div>
                % endif
                </v-box>
            </div>
        </v-box>
    </div>
</template>
"""

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
.text-button {
    font-size: 16px;
    border-radius: 8px;
    color: #333;
    background-color: #fff;
}
.card {
    background-color: #fff;
    border-radius: 12px;
    padding: 10px;
}
.todo {
    /* 未完成任务卡片默认样式（可根据需要补充） */
}
.done {
    /* 已完成任务卡片可额外定义（如淡化背景等） */
    opacity: 0.8;
}
.check-todo {
    border-radius: 15px;
    background-color: #eee;
    border: 2px solid #ccc;
}
.check-done {
    border-radius: 15px;
    background-color: #28a745;
    border: 2px solid #ccc;
}
.task-text {
    font-size: 15px;
    color: #333;
}
.task-text-done {
    font-size: 15px;
    color: #999;
    text-decoration: line-through;
}
.due-text {
    font-size: 12px;
}
.delete-button {
    border-image: url('""" + assetsUrl('icon', 'menu', 'delete.png') + """');
}
.empty-container {
    background-color: #fff;
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

class TodoList(Page):
    def __init__(self):
        super().__init__('todo_list')
        self.template = template
        self.style = STYLE

    def setup(self):
        tasks = self.localStore.get('tasks', [])
        # 深拷贝，避免修改原数据
        tasks = [{**t} for t in tasks]
        # 计算剩余时间和颜色
        now = datetime.now()
        for task in tasks:
            if task['due']:
                due_dt = datetime.fromisoformat(task['due'])
                if task['done']:
                    task['due_str'] = f"已完成（截止 {due_dt.strftime('%Y-%m-%d %H:%M')}）"
                    task['due_color'] = '#28a745'
                else:
                    delta = due_dt - now
                    if delta.total_seconds() < 0:
                        task['due_str'] = f"已逾期 {self._format_delta(-delta)}"
                        task['due_color'] = '#dc3545'
                    elif delta.days < 1:
                        task['due_str'] = f"剩余 {self._format_delta(delta)}"
                        task['due_color'] = '#ffc107'
                    else:
                        task['due_str'] = f"截止 {due_dt.strftime('%Y-%m-%d %H:%M')}"
                        task['due_color'] = '#6c757d'
            else:
                task['due_str'] = '无截止时间'
                task['due_color'] = '#6c757d'

        return {
            's2t': s2t,
            'encode': encode,
            'assetsUrl': assetsUrl,
            'title': f"待办事项 ({len(tasks)})",
            'tasks': tasks,
        }

    def show(self, *args):
        self.register('addTask', 'clicked', self.add_task)
        self.regist_filter(self.click_filter)

    def hide(self, *args):
        tasks = self.localStore.get('tasks', [])
        self.localStore.set('tasks', tasks)

    def add_task(self, *args):
        new_id = generate(size=16)
        new_task = {
            'id': new_id,
            'content': '新任务（双击可编辑）',
            'done': False,
            'due': (datetime.now() + timedelta(hours=24)).isoformat(),
        }
        tasks = self.localStore.get('tasks', [])
        tasks.append(new_task)
        self.localStore.set('tasks', tasks)
        self.rerender(self.setup())
        self.show()

    def click_filter(self, widget: QWidget):
        filter_type = widget.property('event-filter')
        id = widget.property('id')
        if filter_type == 'check-box':
            self.toggle_done(id)
        elif filter_type == 'delete-task':
            self.delete_task(id)

    def toggle_done(self, task_id):
        tasks = self.localStore.get('tasks', [])
        for t in tasks:
            if t['id'] == task_id:
                t['done'] = not t['done']
                break
        self.localStore.set('tasks', tasks)
        self.rerender(self.setup())
        self.show()

    def delete_task(self, task_id):
        tasks = self.localStore.get('tasks', [])
        tasks = [t for t in tasks if t['id'] != task_id]
        self.localStore.set('tasks', tasks)
        self.rerender(self.setup())
        self.show()
        self.tips('任务已删除', 'success')

    def _format_delta(self, delta: timedelta):
        if delta.days > 0:
            return f"{delta.days} 天"
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if hours > 0:
            return f"{hours} 小时 {minutes} 分钟"
        return f"{minutes} 分钟"