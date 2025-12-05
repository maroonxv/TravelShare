"""
app_travel 领域事件定义
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Tuple
import uuid


@dataclass(frozen=True)
class DomainEvent:
    """领域事件基类"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def event_type(self) -> str:
        return self.__class__.__name__


# ==================== 旅行生命周期事件 ====================

@dataclass(frozen=True)
class TripCreatedEvent(DomainEvent):
    """旅行创建事件"""
    trip_id: str = ""
    creator_id: str = ""
    name: str = ""
    start_date: str = ""
    end_date: str = ""


@dataclass(frozen=True)
class TripStartedEvent(DomainEvent):
    """旅行开始事件"""
    trip_id: str = ""
    creator_id: str = ""


@dataclass(frozen=True)
class TripCompletedEvent(DomainEvent):
    """旅行完成事件
    
    跨上下文事件：通知 app_social 可以创建游记
    """
    trip_id: str = ""
    creator_id: str = ""
    name: str = ""


@dataclass(frozen=True)
class TripCancelledEvent(DomainEvent):
    """旅行取消事件"""
    trip_id: str = ""
    reason: Optional[str] = None


@dataclass(frozen=True)
class TripUpdatedEvent(DomainEvent):
    """旅行信息更新事件"""
    trip_id: str = ""
    updated_fields: Tuple[str, ...] = ()


# ==================== 成员管理事件 ====================

@dataclass(frozen=True)
class TripMemberAddedEvent(DomainEvent):
    """成员添加事件"""
    trip_id: str = ""
    user_id: str = ""
    role: str = ""
    added_by: str = ""


@dataclass(frozen=True)
class TripMemberRemovedEvent(DomainEvent):
    """成员移除事件"""
    trip_id: str = ""
    user_id: str = ""
    removed_by: str = ""
    reason: Optional[str] = None


@dataclass(frozen=True)
class TripMemberRoleChangedEvent(DomainEvent):
    """成员角色变更事件"""
    trip_id: str = ""
    user_id: str = ""
    old_role: str = ""
    new_role: str = ""


# ==================== 行程管理事件 ====================

@dataclass(frozen=True)
class ActivityAddedEvent(DomainEvent):
    """活动添加事件"""
    trip_id: str = ""
    day_index: int = 0
    activity_id: str = ""
    activity_name: str = ""


@dataclass(frozen=True)
class ActivityRemovedEvent(DomainEvent):
    """活动移除事件"""
    trip_id: str = ""
    day_index: int = 0
    activity_id: str = ""


@dataclass(frozen=True)
class ActivityUpdatedEvent(DomainEvent):
    """活动更新事件"""
    trip_id: str = ""
    day_index: int = 0
    activity_id: str = ""


@dataclass(frozen=True)
class ItineraryUpdatedEvent(DomainEvent):
    """行程更新事件（批量更新某日行程）"""
    trip_id: str = ""
    day_index: int = 0


@dataclass(frozen=True)
class DayNoteUpdatedEvent(DomainEvent):
    """日程备注更新事件"""
    trip_id: str = ""
    day_index: int = 0
