from datetime import datetime, timedelta
from PySide6.QtWidgets import QWidget, QPushButton, QLineEdit
from app_page import Page
from app_page.utils import encode, assetsUrl
from nanoid import generate


template = """
<template>
    <div class="container">
        <v-box spacing="10" align="AlignTop">
            <!-- 标题和添加按钮 -->
            <div height="40">
                <h-box margins="[0,0,0,0]">
                    <label text="${title}" class="title" />
                    <button id="addTask" text="添加" width="60" height="26" class="primary-button" />
                </h-box>
            </div>

            <!-- 数据统计区域 -->
            <div height="70">
                <h-box spacing="15" align="AlignCenter" margins="[0,0,0,0]">
                    <!-- <button 
                        id="statTodayCreated" 
                        text="今日创建\n${stats['today_created']}" 
                        class="stat-button today ${'active' if filter_type == 'today_created' else ''}" 
                    />
                    <button 
                        id="statTodayDone" 
                        text="今日完成\n${stats['today_done']}" 
                        class="stat-button success ${'active' if filter_type == 'today_done' else ''}" 
                    />
                    <button 
                        id="statTodayTodo" 
                        text="今日未做\n${stats['today_todo']}" 
                        class="stat-button warning ${'active' if filter_type == 'today_todo' else ''}" 
                    /> -->
                    <button 
                        id="statTotalTodo" 
                        text="未完成\n${stats['total_todo']}" 
                        class="stat-button danger ${'active' if filter_type == 'total_todo' else ''}" 
                    />
                    <button 
                        id="statTotalDone" 
                        text="已完成\n${stats['total_done']}" 
                        class="stat-button total ${'active' if filter_type == 'total_done' else ''}" 
                    />
                </h-box>
            </div>

            <!-- 任务列表 -->
            <div>
                <v-box scroll="True" margins="[0,0,0,0]">
                % if len(tasks) > 0:
                    <div>
                        <v-box align="AlignTop" margins="[0,0,0,0]" spacing="10">
                        % for task in tasks:
                            <div class="card ${'done' if task['done'] else 'todo'}" height="75">
                                <h-box spacing="10" margins="[10,0,10,0]" >
                                    <!-- 完成复选框 -->
                                    <button
                                        data-id="${task['id']}"
                                        width="30"
                                        height="30"
                                        event-filter="check-box"
                                        class="${'check-done' if task['done'] else 'check-todo'}"
                                    />

                                    <!-- 任务内容 -->
                                    <div>
                                        <v-box>
                                            <!-- 可编辑的任务内容 -->
                                            <div>
                                                <h-box margins="[0,0,0,0]">
                                                    <button
                                                        id="${task['id']+'-button'}"
                                                        data-id="${task['id']}"
                                                        text="${title_display(task['content'], content_len)}"
                                                        ${title_hover_display(task['content'], content_len)}
                                                        event-filter="edit-content"
                                                        class="task-text ${'done' if task['done'] else ''}"
                                                    />
                                                    <line-edit id="${task['id']+'-edit'}" class="task-text" visible="false" />
                                                    <button id="${task['id']+'-submit'}" text="确定" class="task-handle primary" visible="false" />
                                                    <button id="${task['id']+'-cancel'}" text="取消" class="task-handle default" visible="false" />
                                                </h-box>
                                            </div>
                                            <label text="${encode(task['due_str'])}" class="due-text" style="color:${task['due_color']};" />
                                        </v-box>
                                    </div>

                                    <!-- 标签按钮 -->
                                    <button
                                        data-id="${task['id']}"
                                        width="22"
                                        height="22"
                                        event-filter="label-task"
                                        class="label-button"
                                    />
                                    <!-- 笔记按钮 -->
                                    <button
                                        data-id="${task['id']}"
                                        width="22"
                                        height="22"
                                        event-filter="note-task"
                                        class="note-button"
                                    />
                                    <!-- 删除按钮 -->
                                    <button
                                        data-id="${task['id']}"
                                        width="22"
                                        height="22"
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
.primary-button {
    font-size: 14px;
    border-radius: 8px;
    background-color: #409EFF;
    color: #ffffff;
}
.card {
    background-color: #fff;
    border-radius: 12px;
    padding: 10px;
}
.todo {
    /* 未完成任务卡片默认样式 */
    background-color: #fff;
}
.done {
    /* 已完成任务卡片样式 */
    background-color: rgba(255, 255, 255, 0.5);
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
    text-align: left;
    padding: 0;
    background-color: transparent;
}
.task-text.done {
    text-decoration: line-through;
}
.task-handle {
    background-color: #e0e0e0;
    border-radius: 6px;
    padding: 5px 8px;
}
.task-handle.primary {
    background-color: #409EFF;
    color: #ffffff;
}
.task-handle.default {
    background-color: #f0f0f0;
    color: #ffffff;
}
.due-text {
    font-size: 12px;
}
.delete-button {
    border-image: url('""" + assetsUrl('icon', 'delete.png') + """');
}
.note-button {
    border-image: url('""" + assetsUrl('icon', 'note.png') + """');
}
.label-button {
    border-image: url('""" + assetsUrl('icon', 'label.png') + """');
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

.stat-button {
    width: 100;
    height: 50;
    border-radius: 10px;
    background-color: #e9ecef;
    color: #495057;
    font-size: 14px;
    text-align: center;
    white-space: pre-wrap;
}

.stat-button.success {
    background-color: #d4edda;
    color: #155724;
}

.stat-button.total {
    background-color: #d1ecf1;
    color: #0c5460;
}

.stat-button:hover {
    opacity: 0.8;
}

.stat-button.active {
    font-size: 16px;
    font-weight: bold;
}

.stat-button.today.active {
    background-color: #ffffff;
}

.stat-button.success.active {
    background-color: #a8e6b2;
}

.stat-button.total.active {
    background-color: #a3d8e2;
}

.stat-button.warning {
    background-color: #fff3cd;
    color: #856404;
}

.stat-button.warning.active {
    background-color: #ffeaa7;
}

.stat-button.danger {
    background-color: #f8d7da;
    color: #721c24;
}

.stat-button.danger.active {
    background-color: #f5c6cb;
}
"""

DEFAULT_CONTENT = '新任务（点击可编辑）'

def title_display(title, length=58, is_xml=True):
    ret = title[:length]+"..." if len(title) > length else title
    return encode(ret) if is_xml else ret

def title_hover_display(title, length=58):
    return f'title="{encode(title)}"' if len(title) > length else ''



class TodoList(Page):
    def __init__(self):
        super().__init__('todo-list')
        self.template = template
        self.style = STYLE
        self.is_editing = False
        self.content_len = 45

    def setup(self):
        tasks = self.localStore.get('tasks', [])
        # 当前过滤状态：all / today_created / today_done / total_done
        current_filter = self.localStore.get('current_filter', 'all')
        tasks = [{**t} for t in tasks]

        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day)

        # 统计数据
        today_created = 0
        today_done = 0
        total_done = 0
        today_todo = 0
        total_todo = 0

        display_tasks = []

        for task in tasks:
            created_dt = datetime.fromisoformat(task['created']) if task.get('created') else datetime.min
            done_dt = datetime.fromisoformat(task['done_at']) if task.get('done_at') else None
            is_today_created = created_dt >= today_start

            # 统计
            if created_dt >= today_start:
                today_created += 1
                if not task['done']:
                    today_todo += 1
            if task['done']:
                total_done += 1
                if done_dt and done_dt >= today_start:
                    today_done += 1
            else:
                total_todo += 1

            # 过滤显示逻辑（新增两个条件）
            should_show = True
            if current_filter == 'today_created':
                should_show = is_today_created
            elif current_filter == 'today_done':
                should_show = task['done'] and done_dt and done_dt >= today_start
            elif current_filter == 'total_done':
                should_show = task['done']
            elif current_filter == 'today_todo':
                should_show = is_today_created and not task['done']
            elif current_filter == 'total_todo':
                should_show = not task['done']

            if should_show:
                # 处理 due_str 和颜色（原逻辑不变）
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
                
                display_tasks.append(task)

        return {
            'encode': encode,
            'assetsUrl': assetsUrl,
            'title': f"待办事项 ({len(tasks)})" + (f" - 筛选中" if current_filter != 'all' else ""),
            'tasks': display_tasks,
            'stats': {
                'today_created': today_created,
                'today_done': today_done,
                'total_done': total_done,
                'today_todo': today_todo,
                'total_todo': total_todo,
            },
            'filter_type': current_filter,
            'title_display': title_display,
            'title_hover_display': title_hover_display,
            'content_len': self.content_len,
        }

    def show(self, *args):
        self.register('addTask', 'clicked', self.add_task)
        self.register('statTodayCreated', 'clicked', lambda: self.set_filter('today_created'))
        self.register('statTodayDone', 'clicked', lambda: self.set_filter('today_done'))
        self.register('statTotalDone', 'clicked', lambda: self.set_filter('total_done'))
        self.register('statTodayTodo', 'clicked', lambda: self.set_filter('today_todo'))
        self.register('statTotalTodo', 'clicked', lambda: self.set_filter('total_todo'))
        self.regist_filter(self.click_filter)

    def hide(self, *args):
        tasks = self.localStore.get('tasks', [])
        self.localStore.set('tasks', tasks)

    def set_filter(self, filter_type: str):
        """切换过滤类型，如果点击相同类型则恢复'all'"""
        if self.is_editing:
            self.tips('请先提交编辑', 'warning')
            return
        
        current_filter = self.localStore.get('current_filter', 'all')
        if current_filter == filter_type:
            self.localStore.set('current_filter', 'all') # 再次点击取消
        else:
            self.localStore.set('current_filter', filter_type)

        self.rerender(self.setup())
        self.show()

    def add_task(self, *args):
        if self.is_editing:
            self.tips('请先提交编辑', 'warning')
            return
        
        new_id = generate(size=16)
        new_task = {
            'id': new_id,
            'content': DEFAULT_CONTENT,
            'done': False,
            'due': (datetime.now() + timedelta(hours=24)).isoformat(),
            'created': datetime.now().isoformat(),   # 新增：记录创建时间
        }
        tasks = self.localStore.get('tasks', [])
        tasks.append(new_task)
        self.localStore.set('tasks', tasks)
        self.rerender(self.setup())
        self.show()

    def click_filter(self, widget: QWidget):
        if self.is_editing:
            self.tips('请先提交编辑', 'warning')
            return
        
        filter_type = widget.property('event-filter')
        id = widget.property('data-id')
        if filter_type == 'check-box':
            self.toggle_done(id)
        elif filter_type == 'delete-task':
            self.tipsBox('删除警告', '是否删除当前任务？', '删除后不可恢复', lambda: self.delete_task(id))
        elif filter_type == 'edit-content':
            button: QPushButton = self.getWidget(id + '-button')
            edit: QLineEdit = self.getWidget(id + '-edit')
            submit: QPushButton = self.getWidget(id + '-submit')
            cancel: QPushButton = self.getWidget(id + '-cancel')

            # 获取当前任务文本并填充到编辑框
            tasks = self.localStore.get('tasks', [])
            for t in tasks:
                if t['id'] == id:
                    current_text = t['content']
                    break
            edit.setText(current_text if current_text != DEFAULT_CONTENT else '')

            # 显示编辑控件，隐藏按钮
            button.setVisible(False)
            edit.setVisible(True)
            submit.setVisible(True)
            cancel.setVisible(True)

            self.is_editing = True

            # 从本地存储获取任务列表
            tasks = self.localStore.get('tasks', [])

            def submit_content():
                new_content = edit.toPlainText().strip() if hasattr(edit, 'toPlainText') else edit.text().strip()

                # 如果内容为空，可以选择不修改或提示
                if not new_content:
                    self.tips('内容不能为空', 'warning')
                    return

                for task in tasks:
                    if task.get('id') == id:
                        task['content'] = new_content
                        break

                # 保存回本地存储
                self.localStore.set('tasks', tasks)
                button.setText(title_display(new_content, self.content_len, is_xml=False))
                # 恢复原始状态
                cleanup_editing()

            def cancel_editing():
                cleanup_editing()

            def cleanup_editing():
                button.setVisible(True)
                edit.setVisible(False)
                submit.setVisible(False)
                cancel.setVisible(False)

                # 断开信号避免内存泄漏或多次触发
                submit.clicked.disconnect()
                cancel.clicked.disconnect()

                self.is_editing = False

            # 连接信号（确保之前没连过）
            submit.clicked.connect(submit_content)
            cancel.clicked.connect(cancel_editing)
        else:
            self.tips('正在开发')

    def toggle_done(self, task_id):
        tasks = self.localStore.get('tasks', [])
        for t in tasks:
            if t['id'] == task_id:
                old_done = t['done']
                t['done'] = not t['done']
                # 如果从未完成变为完成，记录完成时间
                if not old_done and t['done']:
                    t['done_at'] = datetime.now().isoformat()
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