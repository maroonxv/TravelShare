"""
通知持久化对象 (PO - Persistent Object)
"""
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Boolean, Index
from shared.database.core import Base

from app_notification.domain.entity.notification import Notification
from app_notification.domain.value_objects.notification_value_objects import (
    NotificationId, NotificationType
)


class NotificationPO(Base):
    """通知持久化对象"""
    
    __tablename__ = 'notifications'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    type = Column(String(30), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    resource_type = Column(String(30), nullable=True)
    resource_id = Column(String(36), nullable=True)
    actor_id = Column(String(36), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 复合索引：用户ID + 创建时间（降序）
    __table_args__ = (
        Index('idx_notifications_user_id_created_at', 'user_id', 'created_at'),
    )
    
    def to_domain(self) -> Notification:
        """转换为领域实体"""
        return Notification(
            id=NotificationId(self.id),
            user_id=self.user_id,
            type=NotificationType.from_string(self.type),
            title=self.title,
            content=self.content,
            resource_type=self.resource_type,
            resource_id=self.resource_id,
            actor_id=self.actor_id,
            is_read=self.is_read,
            created_at=self.created_at
        )
    
    @classmethod
    def from_domain(cls, notification: Notification) -> 'NotificationPO':
        """从领域实体创建"""
        return cls(
            id=notification.id.value,
            user_id=notification.user_id,
            type=notification.type.value,
            title=notification.title,
            content=notification.content,
            resource_type=notification.resource_type,
            resource_id=notification.resource_id,
            actor_id=notification.actor_id,
            is_read=notification.is_read,
            created_at=notification.created_at
        )
