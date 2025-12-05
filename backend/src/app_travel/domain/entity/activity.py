"""
活动实体 - TripDay 的子实体
"""
from dataclasses import dataclass, field
from datetime import time
from typing import Optional
import uuid

from app_travel.domain.value_objects.travel_value_objects import (
    Location, Money, ActivityType, TimeRange
)


@dataclass
class Activity:
    """活动实体
    
    表示旅行中某一天的具体活动，如观光、用餐、交通等。
    作为 TripDay 的子实体存在。
    """
    
    id: str
    name: str
    activity_type: ActivityType
    location: Location
    start_time: time
    end_time: time
    cost: Optional[Money] = None
    notes: str = ""
    booking_reference: Optional[str] = None  # 预订号
    
    @classmethod
    def create(
        cls,
        name: str,
        activity_type: ActivityType,
        location: Location,
        start_time: time,
        end_time: time,
        cost: Optional[Money] = None,
        notes: str = "",
        booking_reference: Optional[str] = None
    ) -> 'Activity':
        """创建新活动"""
        if start_time > end_time:
            raise ValueError("Start time must be before end time")
        
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            activity_type=activity_type,
            location=location,
            start_time=start_time,
            end_time=end_time,
            cost=cost,
            notes=notes,
            booking_reference=booking_reference
        )
    
    @property
    def time_range(self) -> TimeRange:
        """获取时间范围"""
        return TimeRange(self.start_time, self.end_time)
    
    @property
    def duration_minutes(self) -> int:
        """获取活动时长（分钟）"""
        return self.time_range.duration_minutes
    
    def overlaps_with(self, other: 'Activity') -> bool:
        """检查是否与另一个活动时间冲突"""
        return self.time_range.overlaps(other.time_range)
    
    def update(
        self,
        name: Optional[str] = None,
        activity_type: Optional[ActivityType] = None,
        location: Optional[Location] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        cost: Optional[Money] = None,
        notes: Optional[str] = None
    ) -> None:
        """更新活动信息"""
        if name is not None:
            self.name = name
        if activity_type is not None:
            self.activity_type = activity_type
        if location is not None:
            self.location = location
        if start_time is not None:
            self.start_time = start_time
        if end_time is not None:
            self.end_time = end_time
        if cost is not None:
            self.cost = cost
        if notes is not None:
            self.notes = notes
        
        # 验证时间
        if self.start_time > self.end_time:
            raise ValueError("Start time must be before end time")
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Activity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)