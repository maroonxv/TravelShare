"""
通知 DAO 接口
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app_notification.infrastructure.database.persistent_model.notification_po import NotificationPO


class INotificationDAO(ABC):
    """通知 DAO 接口"""
    
    @abstractmethod
    def create(self, notification_po: NotificationPO) -> NotificationPO:
        """创建通知"""
        pass
    
    @abstractmethod
    def get_by_id(self, notification_id: str) -> Optional[NotificationPO]:
        """根据ID获取通知"""
        pass
    
    @abstractmethod
    def get_by_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[NotificationPO]:
        """获取用户的通知列表（分页，按创建时间降序）"""
        pass
    
    @abstractmethod
    def count_unread(self, user_id: str) -> int:
        """统计用户未读通知数量"""
        pass
    
    @abstractmethod
    def update(self, notification_po: NotificationPO) -> NotificationPO:
        """更新通知"""
        pass
    
    @abstractmethod
    def mark_all_read(self, user_id: str) -> int:
        """标记用户所有通知为已读，返回更新数量"""
        pass
