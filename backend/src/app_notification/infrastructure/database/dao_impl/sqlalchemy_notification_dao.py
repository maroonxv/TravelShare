"""
通知 DAO SQLAlchemy 实现
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app_notification.infrastructure.database.dao_interface.i_notification_dao import INotificationDAO
from app_notification.infrastructure.database.persistent_model.notification_po import NotificationPO


class SQLAlchemyNotificationDAO(INotificationDAO):
    """通知 DAO SQLAlchemy 实现"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, notification_po: NotificationPO) -> NotificationPO:
        """创建通知"""
        self.session.add(notification_po)
        self.session.flush()
        return notification_po
    
    def get_by_id(self, notification_id: str) -> Optional[NotificationPO]:
        """根据ID获取通知"""
        return self.session.query(NotificationPO).filter(
            NotificationPO.id == notification_id
        ).first()
    
    def get_by_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[NotificationPO]:
        """获取用户的通知列表（分页，按创建时间降序）"""
        return self.session.query(NotificationPO).filter(
            NotificationPO.user_id == user_id
        ).order_by(NotificationPO.created_at.desc()).limit(limit).offset(offset).all()
    
    def count_unread(self, user_id: str) -> int:
        """统计用户未读通知数量"""
        return self.session.query(NotificationPO).filter(
            NotificationPO.user_id == user_id,
            NotificationPO.is_read == False
        ).count()
    
    def update(self, notification_po: NotificationPO) -> NotificationPO:
        """更新通知"""
        self.session.merge(notification_po)
        self.session.flush()
        return notification_po
    
    def mark_all_read(self, user_id: str) -> int:
        """标记用户所有通知为已读，返回更新数量"""
        count = self.session.query(NotificationPO).filter(
            NotificationPO.user_id == user_id,
            NotificationPO.is_read == False
        ).update({'is_read': True})
        self.session.flush()
        return count
