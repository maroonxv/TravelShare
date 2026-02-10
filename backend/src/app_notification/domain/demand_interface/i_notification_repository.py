"""
通知仓库接口
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app_notification.domain.entity.notification import Notification
from app_notification.domain.value_objects.notification_value_objects import NotificationId


class INotificationRepository(ABC):
    """通知仓库接口"""
    
    @abstractmethod
    def save(self, notification: Notification) -> Notification:
        """保存通知"""
        pass
    
    @abstractmethod
    def find_by_id(self, notification_id: NotificationId) -> Optional[Notification]:
        """根据ID查找通知"""
        pass
    
    @abstractmethod
    def find_by_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Notification]:
        """查找用户的通知列表（分页，按创建时间降序）"""
        pass
    
    @abstractmethod
    def count_unread(self, user_id: str) -> int:
        """统计用户未读通知数量"""
        pass
    
    @abstractmethod
    def mark_all_read(self, user_id: str) -> int:
        """标记用户所有通知为已读，返回更新数量"""
        pass
