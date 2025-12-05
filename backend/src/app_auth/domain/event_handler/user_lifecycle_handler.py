"""
用户生命周期事件处理器

处理用户注册、停用等生命周期事件的副作用。
"""
from typing import Optional

from app_auth.domain.domain_event.user_events import (
    UserRegisteredEvent, UserDeactivatedEvent, UserReactivatedEvent
)


class UserLifecycleHandler:
    """用户生命周期事件处理器
    
    处理：
    - 用户注册后的欢迎通知
    - 用户停用后的清理工作
    - 跨上下文事件转发
    """
    
    def __init__(self, notification_service=None, event_bus=None):
        """
        Args:
            notification_service: 通知服务（可选）
            event_bus: 事件总线，用于发布跨上下文事件（可选）
        """
        self._notification_service = notification_service
        self._event_bus = event_bus
    
    def handle_user_registered(self, event: UserRegisteredEvent) -> None:
        """处理用户注册事件
        
        1. 发送欢迎邮件
        2. 发布跨上下文事件，通知其他限界上下文创建用户档案
        """
        # 发送欢迎邮件
        if self._notification_service:
            self._notification_service.send_email(
                email=event.email,
                subject="欢迎加入旅行分享！",
                body=f"亲爱的 {event.username}，欢迎加入我们的旅行分享社区！"
            )
        
        # 跨上下文事件：通知 app_travel 和 app_social 创建用户档案
        if self._event_bus:
            self._event_bus.publish(event)
    
    def handle_user_deactivated(self, event: UserDeactivatedEvent) -> None:
        """处理用户停用事件
        
        1. 发送账户停用通知
        2. 通知其他上下文处理相关数据
        """
        if self._notification_service:
            self._notification_service.send_email(
                email=event.user_id,  # 需要从 repo 获取邮箱
                subject="账户已停用",
                body=f"您的账户已被停用。原因：{event.reason or '未提供'}"
            )
        
        # 跨上下文事件
        if self._event_bus:
            self._event_bus.publish(event)
    
    def handle_user_reactivated(self, event: UserReactivatedEvent) -> None:
        """处理用户重新激活事件"""
        if self._event_bus:
            self._event_bus.publish(event)
