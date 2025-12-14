"""
旅行日程实体 - Trip 聚合的子实体
"""
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from app_travel.domain.entity.activity import Activity
from app_travel.domain.entity.transit import Transit
from app_travel.domain.entity.itinerary_item import ItineraryItem, ItineraryItemType


@dataclass
class TripDay:
    """旅行日程实体
    
    表示旅行中的某一天，包含该天的所有活动和交通。
    作为 Trip 聚合根的子实体，不能独立存在。
    
    行程顺序：Activity_1 -> Transit_1_2 -> Activity_2 -> Transit_2_3 -> Activity_3 -> ...
    """
    
    day_number: int  # 第几天（从1开始）
    date: date
    theme: Optional[str] = None  # 当日主题（如"古城探索"）
    notes: str = ""  # 备注
    _activities: List[Activity] = field(default_factory=list)
    _transits: List[Transit] = field(default_factory=list)
    
    @classmethod
    def create(cls, day_number: int, d: date, theme: Optional[str] = None) -> 'TripDay':
        """创建日程"""
        if day_number < 1:
            raise ValueError("Day number must be positive")
        return cls(day_number=day_number, date=d, theme=theme)
    
    # ==================== Activity 属性和方法 ====================
    
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
        
        同时移除与该活动相关的所有Transit。
        
        Args:
            activity_id: 活动ID
            
        Returns:
            是否成功移除
        """
        # 查找并移除活动
        activity_found = False
        for i, activity in enumerate(self._activities):
            if activity.id == activity_id:
                self._activities.pop(i)
                activity_found = True
                break
        
        if activity_found:
            # 移除相关的Transit
            self._transits = [
                t for t in self._transits 
                if t.from_activity_id != activity_id and t.to_activity_id != activity_id
            ]
        
        return activity_found
    
    def find_activity(self, activity_id: str) -> Optional[Activity]:
        """查找活动"""
        for activity in self._activities:
            if activity.id == activity_id:
                return activity
        return None
    
    def replace_activities(self, activities: List[Activity]) -> None:
        """替换所有活动（用于批量更新）
        
        同时清空所有Transit，需要重新计算。
        
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
        # 清空Transit，需要重新计算
        self._transits = []
    
    def get_previous_activity(self, activity: Activity) -> Optional[Activity]:
        """获取指定活动的前一个活动"""
        sorted_activities = sorted(self._activities, key=lambda a: a.start_time)
        for i, a in enumerate(sorted_activities):
            if a.id == activity.id and i > 0:
                return sorted_activities[i - 1]
        return None
    
    def get_next_activity(self, activity: Activity) -> Optional[Activity]:
        """获取指定活动的后一个活动"""
        sorted_activities = sorted(self._activities, key=lambda a: a.start_time)
        for i, a in enumerate(sorted_activities):
            if a.id == activity.id and i < len(sorted_activities) - 1:
                return sorted_activities[i + 1]
        return None
    
    def get_activity(self, activity_id: str) -> Optional[Activity]:
        """获取指定活动 (alias for find_activity)"""
        return self.find_activity(activity_id)

    # ==================== Transit 属性和方法 ====================
    
    @property
    def transits(self) -> List[Transit]:
        """获取交通列表的副本"""
        return self._transits.copy()
    
    @property
    def transit_count(self) -> int:
        """获取交通数量"""
        return len(self._transits)
    
    def add_transit(self, transit: Transit) -> None:
        """添加交通
        
        Args:
            transit: 交通实体
        """
        # 检查是否已存在相同起止点的Transit
        for existing in self._transits:
            if (existing.from_activity_id == transit.from_activity_id and 
                existing.to_activity_id == transit.to_activity_id):
                # 替换已存在的Transit
                self._transits.remove(existing)
                break
        
        self._transits.append(transit)
    
    def remove_transit(self, transit_id: str) -> bool:
        """移除交通
        
        Args:
            transit_id: 交通ID
            
        Returns:
            是否成功移除
        """
        for i, transit in enumerate(self._transits):
            if transit.id == transit_id:
                self._transits.pop(i)
                return True
        return False
    
    def remove_transit_between(self, from_activity_id: str, to_activity_id: str) -> bool:
        """移除两个活动之间的交通
        
        Args:
            from_activity_id: 起始活动ID
            to_activity_id: 目标活动ID
            
        Returns:
            是否成功移除
        """
        for i, transit in enumerate(self._transits):
            if (transit.from_activity_id == from_activity_id and 
                transit.to_activity_id == to_activity_id):
                self._transits.pop(i)
                return True
        return False
    
    def get_transit_between(self, from_activity_id: str, to_activity_id: str) -> Optional[Transit]:
        """获取两个活动之间的交通
        
        Args:
            from_activity_id: 起始活动ID
            to_activity_id: 目标活动ID
            
        Returns:
            Transit 或 None
        """
        for transit in self._transits:
            if (transit.from_activity_id == from_activity_id and 
                transit.to_activity_id == to_activity_id):
                return transit
        return None
    
    def replace_transits(self, transits: List[Transit]) -> None:
        """替换所有交通
        
        Args:
            transits: 新的交通列表
        """
        self._transits = transits.copy()
    
    # ==================== 有序行程方法 ====================
    
    def get_ordered_itinerary(self) -> List[ItineraryItem]:
        """获取有序的行程列表
        
        按时间顺序返回 Activity 和 Transit 交替的列表。
        顺序：Activity_1 -> Transit_1_2 -> Activity_2 -> Transit_2_3 -> ...
        
        Returns:
            List[ItineraryItem]: 有序的行程项列表
        """
        items: List[ItineraryItem] = []
        sorted_activities = sorted(self._activities, key=lambda a: a.start_time)
        sequence = 0
        
        for i, activity in enumerate(sorted_activities):
            # 添加 Activity
            items.append(ItineraryItem.from_activity(sequence, activity))
            sequence += 1
            
            # 如果不是最后一个活动，查找对应的 Transit
            if i < len(sorted_activities) - 1:
                next_activity = sorted_activities[i + 1]
                transit = self.get_transit_between(activity.id, next_activity.id)
                if transit:
                    items.append(ItineraryItem.from_transit(sequence, transit))
                    sequence += 1
        
        return items
    
    # ==================== 统计方法 ====================
    
    def calculate_total_cost(self) -> 'Money':
        """计算当日总花费（活动 + 交通）"""
        from app_travel.domain.value_objects.travel_value_objects import Money
        
        total = Money.zero()
        
        # 活动费用
        for activity in self._activities:
            if activity.cost:
                total = total + activity.cost
        
        # 交通费用
        for transit in self._transits:
            if transit.estimated_cost:
                total = total + transit.estimated_cost.estimated_cost
        
        return total
    
    def calculate_activity_cost(self) -> 'Money':
        """计算当日活动花费"""
        from app_travel.domain.value_objects.travel_value_objects import Money
        
        total = Money.zero()
        for activity in self._activities:
            if activity.cost:
                total = total + activity.cost
        return total
    
    def calculate_transit_cost(self) -> 'Money':
        """计算当日交通花费"""
        from app_travel.domain.value_objects.travel_value_objects import Money
        
        total = Money.zero()
        for transit in self._transits:
            if transit.estimated_cost:
                total = total + transit.estimated_cost.estimated_cost
        return total
    
    def calculate_total_transit_time(self) -> int:
        """计算当日总交通时间（分钟）"""
        return sum(t.duration_minutes for t in self._transits)
    
    def calculate_total_transit_distance(self) -> float:
        """计算当日总交通距离（米）"""
        return sum(t.distance_meters for t in self._transits)
    
    def calculate_total_play_time(self) -> int:
        """计算当日总游玩时间（分钟）"""
        return sum(a.duration_minutes for a in self._activities)
    
    # ==================== 其他方法 ====================
    
    def update_theme(self, theme: Optional[str]) -> None:
        """更新主题"""
        self.theme = theme
    
    def update_notes(self, notes: str) -> None:
        """更新备注"""
        self.notes = notes
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TripDay):
            return False
        return self.day_number == other.day_number and self.date == other.date
    
    def __hash__(self) -> int:
        return hash((self.day_number, self.date))
