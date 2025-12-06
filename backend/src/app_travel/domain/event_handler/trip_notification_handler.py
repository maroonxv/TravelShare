"""
旅行通知事件处理器

处理旅行成员变更等需要通知的事件。
"""
from typing import Optional

from app_travel.domain.domain_event.travel_events import (
    TripMemberAddedEvent, TripMemberRemovedEvent, TripMemberRoleChangedEvent,
    TripStartedEvent, TripCancelledEvent
)


class TripNotificationHandler:
    """旅行通知事件处理器
    
    处理：
    - 成员添加通知
    - 成员移除通知
    - 旅行开始/取消通知
    """
    
    def __init__(self, notification_service=None, user_service=None):
        """
        Args:
            notification_service: 通知服务
            user_service: 用户服务（获取用户信息）
        """
        self._notification_service = notification_service
        self._user_service = user_service
    
    def handle_member_added(self, event: TripMemberAddedEvent) -> None:
        """处理成员添加事件
        
        通知被添加的用户。
        """
        if self._notification_service:
            self._notification_service.send_push(
                user_id=event.user_id,
                title="您已加入旅行",
                body=f"您已被添加到旅行中，角色：{event.role}",
                data={"trip_id": event.trip_id}
            )
    
    def handle_member_removed(self, event: TripMemberRemovedEvent) -> None:
        """处理成员移除事件
        
        通知被移除的用户。
        """
        if self._notification_service:
            body = "您已被移出旅行"
            if event.reason:
                body += f"，原因：{event.reason}"
            
            self._notification_service.send_push(
                user_id=event.user_id,
                title="旅行成员变更",
                body=body,
                data={"trip_id": event.trip_id}
            )
    
    def handle_role_changed(self, event: TripMemberRoleChangedEvent) -> None:
        """处理角色变更事件"""
        if self._notification_service:
            self._notification_service.send_push(
                user_id=event.user_id,
                title="角色变更",
                body=f"您的角色已从 {event.old_role} 变更为 {event.new_role}",
                data={"trip_id": event.trip_id}
            )
    
    def handle_trip_started(self, event: TripStartedEvent) -> None:
        """处理旅行开始事件
        
        通知所有成员旅行已开始。
        """
        # TODO：需要从 repository 获取成员列表
        # 这里仅作为示例
        pass
    
    def handle_trip_cancelled(self, event: TripCancelledEvent) -> None:
        """处理旅行取消事件
        
        通知所有成员旅行已取消。
        """
        # TODO
        pass
