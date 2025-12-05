"""
旅行完成事件处理器

处理旅行完成后的跨上下文操作。
"""
from app_travel.domain.domain_event.travel_events import TripCompletedEvent


class TripCompletionHandler:
    """旅行完成事件处理器
    
    处理旅行完成后的业务逻辑：
    - 发布跨上下文事件，通知 app_social 可以创建游记
    - 发送完成通知给所有成员
    """
    
    def __init__(self, event_bus=None, notification_service=None):
        """
        Args:
            event_bus: 事件总线，用于发布跨上下文事件
            notification_service: 通知服务
        """
        self._event_bus = event_bus
        self._notification_service = notification_service
    
    def handle_trip_completed(self, event: TripCompletedEvent) -> None:
        """处理旅行完成事件
        
        1. 发布跨上下文事件给 app_social
        2. 通知创建者可以写游记
        """
        # 发布跨上下文事件
        if self._event_bus:
            self._event_bus.publish(event)
        
        # 通知创建者
        if self._notification_service:
            self._notification_service.send_push(
                user_id=event.creator_id,
                title="旅行已完成 🎉",
                body=f"您的旅行「{event.name}」已完成！点击分享您的旅行故事。",
                data={
                    "trip_id": event.trip_id,
                    "action": "create_travel_log"
                }
            )
