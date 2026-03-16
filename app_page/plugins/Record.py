# 记录管理器 (优化版)
from typing import List, Optional

class Record:
    """记录管理器类，用于管理ID列表和遍历操作"""
    
    def __init__(self, max_records: int = 50) -> None:
        """初始化记录管理器
        
        Args:
            max_records: 最大记录数量，超过此限制会自动移除最早记录
        """
        self._max_records = max_records
        self._record_list: List[str] = []
        self._current_index: int = -1
    
    @property
    def count(self) -> int:
        """获取当前记录数量"""
        return len(self._record_list)
    
    def add_record(self, record_id: str) -> None:
        """添加新记录
        
        Args:
            record_id: 要添加的记录ID
        """
        if not isinstance(record_id, str):
            raise ValueError("record_id必须是字符串")
        
        # 超出限制则移除最早的记录
        if len(self._record_list) >= self._max_records:
            self._record_list.pop(0)
        
        self._record_list.append(record_id)
        self._current_index = -1
    
    def get_record(self, index: Optional[int] = None) -> Optional[str]:
        """根据索引获取记录
        
        Args:
            index: 索引位置，None表示获取最新记录
            
        Returns:
            对应索引的记录，如果不存在返回None
        """
        if not self._record_list:
            return None
            
        if index is None or index == -1:
            return self._record_list[-1]
        
        if 0 <= index < len(self._record_list):
            return self._record_list[index]
        
        return None
    
    def get_current(self) -> Optional[str]:
        """获取当前索引位置的记录"""
        if self._current_index == -1 or not self._record_list:
            return None
        return self._record_list[self._current_index]
    
    def move_left(self) -> Optional[str]:
        """向左移动索引并返回对应记录"""
        if not self._record_list:
            return None
        
        if self._current_index == -1:
            self._current_index = len(self._record_list) - 1
        elif self._current_index > 0:
            self._current_index -= 1
        
        return self._record_list[self._current_index]
    
    def move_right(self) -> Optional[str]:
        """向右移动索引并返回对应记录"""
        if not self._record_list:
            return None
        
        if self._current_index == -1:
            self._current_index = 0
        elif self._current_index < len(self._record_list) - 1:
            self._current_index += 1
        
        return self._record_list[self._current_index]
    
    def clear(self) -> None:
        """清空所有记录"""
        self._record_list.clear()
        self._current_index = -1
    
    def contains(self, record_id: str) -> bool:
        """检查记录是否存在"""
        return record_id in self._record_list
    
    def get_all(self) -> List[str]:
        """获取所有记录的副本"""
        return self._record_list.copy()
    
    def __len__(self) -> int:
        """返回记录数量"""
        return len(self._record_list)
    
    def __repr__(self) -> str:
        """对象字符串表示"""
        return f"Record(count={len(self._record_list)}, max={self._max_records})"