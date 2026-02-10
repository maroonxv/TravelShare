"""
通知应用服务
"""
from typing import List, Dict, Any

from app_notification.domain.demand_interface.i_notification_repository import INotificationRepository
from app_notification.domain.value_objects.notification_value_objects import NotificationId


class NotificationService:
    """通知应用服务"""
    
    def __init__(self, notification_repository: INotificationRepository):
        self._notification_repository = notification_repository
    
    def get_notifications(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """获取用户通知列表
        
        Args:
            user_id: 用户ID
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            通知列表
        """
        notifications = self._notification_repository.find_by_user(user_id, limit, offset)
        
        return [
            {
                'id': n.id.value,
                'type': n.type.value,
                'title': n.title,
                'content': n.content,
                'resource_type': n.resource_type,
                'resource_id': n.resource_id,
                'actor_id': n.actor_id,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat()
            }
            for n in notifications
        ]
    
    def get_unread_count(self, user_id: str) -> int:
        """获取未读通知数量
        
        Args:
            user_id: 用户ID
            
        Returns:
            未读数量
        """
        return self._notification_repository.count_unread(user_id)
    
    def mark_read(self, notification_id: str, user_id: str) -> bool:
        """标记单条通知已读
        
        Args:
            notification_id: 通知ID
            user_id: 用户ID（用于验证权限）
            
        Returns:
            是否成功
        """
        notification = self._notification_repository.find_by_id(NotificationId(notification_id))
        
        if not notification:
            return False
        
        # 验证权限
        if notification.user_id != user_id:
            return False
        
        notification.mark_as_read()
        self._notification_repository.save(notification)
        
        return True
    
    def mark_all_read(self, user_id: str) -> int:
        """标记全部通知已读
        
        Args:
            user_id: 用户ID
            
        Returns:
            更新数量
        """
        return self._notification_repository.mark_all_read(user_id)
