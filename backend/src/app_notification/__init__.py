"""
app_notification - 通知中心模块

提供站内通知功能。
"""
from app_notification.domain.event_handler.notification_event_handler import register_notification_handlers

# 注册事件处理器
register_notification_handlers()
