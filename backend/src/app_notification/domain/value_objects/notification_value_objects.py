"""
通知相关值对象
"""
from dataclasses import dataclass
from enum import Enum
import uuid


class NotificationType(Enum):
    """通知类型枚举"""
    FRIEND_REQUEST = "friend_request"
    FRIEND_ACCEPTED = "friend_accepted"
    TRIP_INVITE = "trip_invite"
    POST_LIKED = "post_liked"
    POST_COMMENTED = "post_commented"
    EXPENSE_ADDED = "expense_added"
    
    @classmethod
    def from_string(cls, type_str: str) -> 'NotificationType':
        type_str = type_str.lower()
        for ntype in cls:
            if ntype.value == type_str:
                return ntype
        raise ValueError(f"Unknown notification type: {type_str}")


@dataclass(frozen=True)
class NotificationId:
    """通知唯一标识"""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("NotificationId cannot be empty")
    
    @classmethod
    def generate(cls) -> 'NotificationId':
        return cls(str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value
