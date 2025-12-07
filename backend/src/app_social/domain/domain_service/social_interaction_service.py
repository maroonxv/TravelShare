"""
社交互动领域服务

处理需要跨聚合协调的社交操作。
"""
from typing import List

from app_social.domain.aggregate.post_aggregate import Post
from app_social.domain.aggregate.conversation_aggregate import Conversation
from app_social.domain.value_objects.social_value_objects import MessageContent


class SocialInteractionService:
    """社交互动领域服务 - 纯业务逻辑
    
    处理需要跨聚合协调的操作，如分享帖子到会话。
    不再包含基础设施依赖（Repository），只负责协调聚合根之间的状态变更。
    """
    
    def share_post_to_conversation(
        self,
        post: Post,
        conversation: Conversation,
        sharer_id: str,
        message: str = ""
    ) -> None:
        """分享帖子到会话
        
        前提：调用方需确保 sharer_id 有权限查看 post。
        
        Args:
            post: 帖子聚合根
            conversation: 会话聚合根
            sharer_id: 分享者ID
            message: 附加消息（可选）
            
        Raises:
            ValueError: 如果分享者不在会话中
        """
        if not conversation.is_participant(sharer_id):
            raise ValueError("Not a participant of this conversation")
        
        # 发送分享消息
        content = MessageContent.trip_share_message(
            trip_id=post.id.value,
            message=message or f"分享了帖子：{post.content.title}"
        )
        conversation.send_message(sharer_id, content)
        
        # 记录分享事件
        recipient_ids = [p for p in conversation.participant_ids if p != sharer_id]
        post.share_to(sharer_id, recipient_ids)
    
    def share_post_to_conversations(
        self,
        post: Post,
        conversations: List[Conversation],
        sharer_id: str
    ) -> None:
        """批量分享帖子到多个会话
        
        Args:
            post: 帖子聚合根
            conversations: 目标会话列表
            sharer_id: 分享者ID
        """
        for conversation in conversations:
            self.share_post_to_conversation(
                post=post,
                conversation=conversation,
                sharer_id=sharer_id
            )
