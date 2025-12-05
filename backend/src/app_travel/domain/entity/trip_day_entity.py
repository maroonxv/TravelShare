"""
旅行日程实体 - Trip 聚合的子实体
"""
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from app_travel.domain.entity.activity import Activity


@dataclass
class TripDay:
    """旅行日程实体
    
    表示旅行中的某一天，包含该天的所有活动。
    作为 Trip 聚合根的子实体，不能独立存在。
    """
    
    day_number: int  # 第几天（从1开始）
    date: date
    theme: Optional[str] = None  # 当日主题（如"古城探索"）
    notes: str = ""  # 备注
    _activities: List[Activity] = field(default_factory=list)
    
    @classmethod
    def create(cls, day_number: int, d: date, theme: Optional[str] = None) -> 'TripDay':
        """创建日程"""
        if day_number < 1:
            raise ValueError("Day number must be positive")
        return cls(day_number=day_number, date=d, theme=theme)
    
    @property
    def activities(self) -> List[Activity]:
        """获取活动列表的副本"""
        return self._activities.copy()
    
    @property
    def activity_count(self) -> int:
        """获取活动数量"""
        return len(self._activities)
    
    def add_activity(self, activity: Activity) -> None:
        """添加活动
        
        Args:
            activity: 活动实体
            
        Raises:
            ValueError: 如果与现有活动时间冲突
        """
        # 检查时间冲突
        for existing in self._activities:
            if existing.overlaps_with(activity):
                raise ValueError(
                    f"Activity '{activity.name}' conflicts with '{existing.name}'"
                )
        
        self._activities.append(activity)
        # 按开始时间排序
        self._activities.sort(key=lambda a: a.start_time)
    
    def remove_activity(self, activity_id: str) -> bool:
        """移除活动
        
        Args:
            activity_id: 活动ID
            
        Returns:
            是否成功移除
        """
        for i, activity in enumerate(self._activities):
            if activity.id == activity_id:
                self._activities.pop(i)
                return True
        return False
    
    def find_activity(self, activity_id: str) -> Optional[Activity]:
        """查找活动"""
        for activity in self._activities:
            if activity.id == activity_id:
                return activity
        return None
    
    def replace_activities(self, activities: List[Activity]) -> None:
        """替换所有活动（用于批量更新）
        
        Args:
            activities: 新的活动列表
        """
        # 检查新活动之间是否有冲突
        sorted_activities = sorted(activities, key=lambda a: a.start_time)
        for i in range(len(sorted_activities) - 1):
            if sorted_activities[i].overlaps_with(sorted_activities[i + 1]):
                raise ValueError(
                    f"Activities '{sorted_activities[i].name}' and "
                    f"'{sorted_activities[i + 1].name}' have time conflict"
                )
        
        self._activities = sorted_activities
    
    def update_theme(self, theme: Optional[str]) -> None:
        """更新主题"""
        self.theme = theme
    
    def update_notes(self, notes: str) -> None:
        """更新备注"""
        self.notes = notes
    
    def calculate_total_cost(self) -> 'Money':
        """计算当日总花费"""
        from app_travel.domain.value_objects.travel_value_objects import Money
        
        total = Money.zero()
        for activity in self._activities:
            if activity.cost:
                total = total + activity.cost
        return total
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TripDay):
            return False
        return self.day_number == other.day_number and self.date == other.date
    
    def __hash__(self) -> int:
        return hash((self.day_number, self.date))
