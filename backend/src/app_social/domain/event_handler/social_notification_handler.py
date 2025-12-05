"""
社交通知事件处理器

处理社交互动（评论、点赞、私信）的通知。
"""
from typing import Optional

from app_social.domain.domain_event.social_events import (
    CommentAddedEvent, PostLikedEvent, MessageSentEvent, PostSharedEvent
)
from app_social.domain.demand_interface.i_notification_service import INotificationService


class SocialNotificationHandler:
    """社交通知事件处理器
    
    处理：
    - 评论通知
    - 点赞通知
    - 私信通知
    - 分享通知
    """
    
    def __init__(self, notification_service: Optional[INotificationService] = None):
        """
        Args:
            notification_service: 通知服务
        """
        self._notification_service = notification_service
    
    def handle_comment_added(self, event: CommentAddedEvent) -> None:
        """处理评论添加事件
        
        通知帖子作者有新评论（自己评论自己的帖子不通知）。
        """
        if not self._notification_service:
            return
        
        # 不通知自己
        if event.author_id == event.post_author_id:
            return
        
        if event.parent_comment_id:
            # 回复评论
            title = "有人回复了您的评论"
            body = "有人回复了您在帖子中的评论，点击查看"
        else:
            # 直接评论帖子
            title = "有人评论了您的帖子"
            body = "您的帖子收到了新评论，点击查看"
        
        self._notification_service.send_push(
            user_id=event.post_author_id,
            title=title,
            body=body,
            data={
                "type": "comment",
                "post_id": event.post_id,
                "comment_id": event.comment_id
            }
        )
    
    def handle_post_liked(self, event: PostLikedEvent) -> None:
        """处理点赞事件
        
        通知帖子作者有新点赞（自己点赞自己的帖子不通知）。
        """
        if not self._notification_service:
            return
        
        # 不通知自己
        if event.user_id == event.post_author_id:
            return
        
        self._notification_service.send_push(
            user_id=event.post_author_id,
            title="有人点赞了您的帖子 ❤️",
            body="您的帖子收到了新的点赞",
            data={
                "type": "like",
                "post_id": event.post_id,
                "user_id": event.user_id
            }
        )
    
    def handle_message_sent(self, event: MessageSentEvent) -> None:
        """处理消息发送事件
        
        通知所有接收者有新消息。
        """
        if not self._notification_service:
            return
        
        for recipient_id in event.recipient_ids:
            self._notification_service.send_push(
                user_id=recipient_id,
                title="您有新消息",
                body="您收到了一条新私信，点击查看",
                data={
                    "type": "message",
                    "conversation_id": event.conversation_id,
                    "message_id": event.message_id,
                    "sender_id": event.sender_id
                }
            )
    
    def handle_post_shared(self, event: PostSharedEvent) -> None:
        """处理帖子分享事件
        
        通知被分享的用户。
        """
        if not self._notification_service:
            return
        
        for recipient_id in event.shared_to_ids:
            self._notification_service.send_push(
                user_id=recipient_id,
                title="有人向您分享了帖子",
                body="有朋友向您分享了一篇帖子，点击查看",
                data={
                    "type": "share",
                    "post_id": event.post_id,
                    "sharer_id": event.sharer_id
                }
            )
