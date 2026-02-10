"""
通知仓库实现
"""
from typing import List, Optional

from app_notification.domain.entity.notification import Notification
from app_notification.domain.value_objects.notification_value_objects import NotificationId
from app_notification.domain.demand_interface.i_notification_repository import INotificationRepository
from app_notification.infrastructure.database.dao_interface.i_notification_dao import INotificationDAO
from app_notification.infrastructure.database.persistent_model.notification_po import NotificationPO


class NotificationRepositoryImpl(INotificationRepository):
    """通知仓库实现"""
    
    def __init__(self, dao: INotificationDAO):
        self._dao = dao
    
    def save(self, notification: Notification) -> Notification:
        """保存通知"""
        po = NotificationPO.from_domain(notification)
        
        # 检查是否已存在
        existing = self._dao.get_by_id(notification.id.value)
        if existing:
            # 更新
            existing.is_read = notification.is_read
            self._dao.update(existing)
        else:
            # 创建
            self._dao.create(po)
        
        return notification
    
    def find_by_id(self, notification_id: NotificationId) -> Optional[Notification]:
        """根据ID查找通知"""
        po = self._dao.get_by_id(notification_id.value)
        return po.to_domain() if po else None
    
    def find_by_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Notification]:
        """查找用户的通知列表（分页，按创建时间降序）"""
        pos = self._dao.get_by_user(user_id, limit, offset)
        return [po.to_domain() for po in pos]
    
    def count_unread(self, user_id: str) -> int:
        """统计用户未读通知数量"""
        return self._dao.count_unread(user_id)
    
    def mark_all_read(self, user_id: str) -> int:
        """标记用户所有通知为已读，返回更新数量"""
        return self._dao.mark_all_read(user_id)
