class PanelStore:
    def __init__(self):
        self.panel = None

    def close(self):
        """安全关闭并清理面板引用"""
        if self.panel:
            # 使用 getattr 配合可调用检查，比 hasattr 更严谨
            destroy_method = getattr(self.panel, 'destroy', None)
            if callable(destroy_method):
                destroy_method()
            self.panel = None
    
    def add(self, panel):
        """添加新面板前先尝试关闭旧面板"""
        if self.panel is not panel:  # 避免重复添加同一个面板
            self.close()
            self.panel = panel
