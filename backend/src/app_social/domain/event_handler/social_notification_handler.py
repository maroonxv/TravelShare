"""
社交通知事件处理器

处理社交互动（评论、点赞、私信）的通知。
"""
from typing import Optional

from app_social.domain.domain_event.social_events import (
    CommentAddedEvent, PostLikedEvent, MessageSentEvent, PostSharedEvent
)


class SocialNotificationHandler:
    """社交通知事件处理器
    
    处理：
    - 评论通知
    - 点赞通知
    - 私信通知
    - 分享通知
    """
    
    def __init__(self):
        pass
    
    def handle_comment_added(self, event: CommentAddedEvent) -> None:
        """处理评论添加事件
        
        通知帖子作者有新评论（自己评论自己的帖子不通知）。
        """
        # 不通知自己
        if event.author_id == event.post_author_id:
            return
        
        if event.parent_comment_id:
            # 回复评论
            print(f"[Notification] User {event.post_author_id}: 有人回复了您的评论")
        else:
            # 直接评论帖子
            print(f"[Notification] User {event.post_author_id}: 有人评论了您的帖子")
    
    def handle_post_liked(self, event: PostLikedEvent) -> None:
        """处理点赞事件
        
        通知帖子作者有新点赞（自己点赞自己的帖子不通知）。
        """
        # 不通知自己
        if event.user_id == event.post_author_id:
            return
        
        print(f"[Notification] User {event.post_author_id}: 有人点赞了您的帖子 ❤️")
    
    def handle_message_sent(self, event: MessageSentEvent) -> None:
        """处理消息发送事件
        
        通知所有接收者有新消息。
        """
        for recipient_id in event.recipient_ids:
            print(f"[Notification] User {recipient_id}: 您有新消息")
    
    def handle_post_shared(self, event: PostSharedEvent) -> None:
        """处理帖子分享事件
        
        通知被分享的用户。
        """
        for recipient_id in event.shared_to_ids:
            print(f"[Notification] User {recipient_id}: 有人向您分享了帖子")
