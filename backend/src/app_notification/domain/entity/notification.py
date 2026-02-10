"""
通知实体
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app_notification.domain.value_objects.notification_value_objects import (
    NotificationId, NotificationType
)


@dataclass
class Notification:
    """通知实体
    
    表示一条站内通知消息。
    """
    
    id: NotificationId
    user_id: str               # 接收者
    type: NotificationType     # 通知类型
    title: str                 # 通知标题
    content: str               # 通知内容
    resource_type: Optional[str] = None  # 关联资源类型 (trip, post, user, expense)
    resource_id: Optional[str] = None    # 关联资源 ID
    actor_id: Optional[str] = None       # 触发者 ID
    is_read: bool = False      # 已读状态
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.utcnow())
    
    @classmethod
    def create(
        cls,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        content: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        actor_id: Optional[str] = None
    ) -> 'Notification':
        """创建新通知
        
        Args:
            user_id: 接收者ID
            notification_type: 通知类型
            title: 标题
            content: 内容
            resource_type: 关联资源类型
            resource_id: 关联资源ID
            actor_id: 触发者ID
            
        Returns:
            Notification: 新创建的通知实体
        """
        return cls(
            id=NotificationId.generate(),
            user_id=user_id,
            type=notification_type,
            title=title,
            content=content,
            resource_type=resource_type,
            resource_id=resource_id,
            actor_id=actor_id,
            is_read=False,
            created_at=datetime.utcnow()
        )
    
    def mark_as_read(self) -> None:
        """标记为已读"""
        self.is_read = True
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Notification):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id.value)
