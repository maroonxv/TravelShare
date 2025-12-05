"""
app_travel 值对象定义

包含旅行相关的所有值对象。
"""
from dataclasses import dataclass, field
from datetime import date, time, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
import uuid


@dataclass(frozen=True)
class TripId:
    """旅行唯一标识"""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("TripId cannot be empty")
    
    @classmethod
    def generate(cls) -> 'TripId':
        return cls(str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TripName:
    """旅行名称"""
    value: str
    
    MIN_LENGTH = 1
    MAX_LENGTH = 100
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("TripName cannot be empty")
        if len(self.value) > self.MAX_LENGTH:
            raise ValueError(f"TripName must be at most {self.MAX_LENGTH} characters")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TripDescription:
    """旅行描述"""
    value: str
    
    MAX_LENGTH = 2000
    
    def __post_init__(self):
        if self.value and len(self.value) > self.MAX_LENGTH:
            raise ValueError(f"TripDescription must be at most {self.MAX_LENGTH} characters")
    
    def __str__(self) -> str:
        return self.value or ""


@dataclass(frozen=True)
class DateRange:
    """日期范围值对象"""
    start_date: date
    end_date: date
    
    def __post_init__(self):
        if self.start_date > self.end_date:
            raise ValueError("Start date must be before or equal to end date")
    
    @property
    def days(self) -> int:
        """获取天数"""
        return (self.end_date - self.start_date).days + 1
    
    def contains(self, d: date) -> bool:
        """检查日期是否在范围内"""
        return self.start_date <= d <= self.end_date
    
    def overlaps(self, other: 'DateRange') -> bool:
        """检查两个日期范围是否重叠"""
        return self.start_date <= other.end_date and other.start_date <= self.end_date


@dataclass(frozen=True)
class Location:
    """位置信息值对象"""
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Location name cannot be empty")
        if self.latitude is not None and (self.latitude < -90 or self.latitude > 90):
            raise ValueError("Latitude must be between -90 and 90")
        if self.longitude is not None and (self.longitude < -180 or self.longitude > 180):
            raise ValueError("Longitude must be between -180 and 180")
    
    def __str__(self) -> str:
        return self.name
    
    def has_coordinates(self) -> bool:
        """是否包含坐标信息"""
        return self.latitude is not None and self.longitude is not None


@dataclass(frozen=True)
class Money:
    """货币金额值对象"""
    amount: Decimal
    currency: str = "CNY"
    
    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
    
    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot add different currencies: {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)
    
    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"
    
    @classmethod
    def zero(cls, currency: str = "CNY") -> 'Money':
        return cls(Decimal("0"), currency)


@dataclass(frozen=True)
class TimeRange:
    """时间范围值对象（一天内的时间）"""
    start_time: time
    end_time: time
    
    def __post_init__(self):
        if self.start_time > self.end_time:
            raise ValueError("Start time must be before or equal to end time")
    
    @property
    def duration_minutes(self) -> int:
        """获取时长（分钟）"""
        start = datetime.combine(date.today(), self.start_time)
        end = datetime.combine(date.today(), self.end_time)
        return int((end - start).total_seconds() / 60)
    
    def overlaps(self, other: 'TimeRange') -> bool:
        """检查两个时间范围是否重叠"""
        return self.start_time < other.end_time and other.start_time < self.end_time


class TripStatus(Enum):
    """旅行状态枚举"""
    PLANNING = "planning"       # 计划中
    IN_PROGRESS = "in_progress" # 进行中
    COMPLETED = "completed"     # 已完成
    CANCELLED = "cancelled"     # 已取消
    
    @classmethod
    def from_string(cls, status_str: str) -> 'TripStatus':
        status_str = status_str.lower()
        for status in cls:
            if status.value == status_str:
                return status
        raise ValueError(f"Unknown status: {status_str}")


class TripVisibility(Enum):
    """旅行可见性枚举"""
    PRIVATE = "private"   # 仅自己可见
    FRIENDS = "friends"   # 好友可见
    PUBLIC = "public"     # 公开
    
    @classmethod
    def from_string(cls, visibility_str: str) -> 'TripVisibility':
        visibility_str = visibility_str.lower()
        for visibility in cls:
            if visibility.value == visibility_str:
                return visibility
        raise ValueError(f"Unknown visibility: {visibility_str}")


class MemberRole(Enum):
    """成员角色枚举"""
    ADMIN = "admin"   # 管理员（创建者）
    MEMBER = "member" # 普通成员
    
    @classmethod
    def from_string(cls, role_str: str) -> 'MemberRole':
        role_str = role_str.lower()
        for role in cls:
            if role.value == role_str:
                return role
        raise ValueError(f"Unknown role: {role_str}")


class ActivityType(Enum):
    """活动类型枚举"""
    TRANSPORT = "transport"       # 交通
    DINING = "dining"             # 餐饮
    SIGHTSEEING = "sightseeing"   # 观光
    ACCOMMODATION = "accommodation" # 住宿
    SHOPPING = "shopping"         # 购物
    ENTERTAINMENT = "entertainment" # 娱乐
    OTHER = "other"               # 其他
    
    @classmethod
    def from_string(cls, type_str: str) -> 'ActivityType':
        type_str = type_str.lower()
        for activity_type in cls:
            if activity_type.value == type_str:
                return activity_type
        raise ValueError(f"Unknown activity type: {type_str}")
