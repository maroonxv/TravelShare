"""
社交互动领域服务

处理需要跨聚合协调的社交操作。
"""
from typing import List, Optional

from app_social.domain.aggregate.post_aggregate import Post
from app_social.domain.aggregate.conversation_aggregate import Conversation
from app_social.domain.value_objects.social_value_objects import (
    PostId, PostContent, PostVisibility, MessageContent
)
from app_social.domain.demand_interface.i_post_repository import IPostRepository
from app_social.domain.demand_interface.i_conversation_repository import IConversationRepository


class SocialInteractionService:
    """社交互动领域服务 - 无状态
    
    处理需要跨聚合协调的操作，如分享帖子到会话。
    """
    
    def __init__(
        self,
        post_repo: IPostRepository,
        conversation_repo: IConversationRepository
    ):
        self._post_repo = post_repo
        self._conversation_repo = conversation_repo
    
    def share_post_to_conversation(
        self,
        post_id: PostId,
        sharer_id: str,
        conversation_id: str,
        message: str = ""
    ) -> None:
        """分享帖子到会话
        
        Args:
            post_id: 帖子ID
            sharer_id: 分享者ID
            conversation_id: 目标会话ID
            message: 附加消息（可选）
        """
        from app_social.domain.value_objects.social_value_objects import ConversationId
        
        # 获取帖子
        post = self._post_repo.find_by_id(post_id)
        if not post:
            raise ValueError("Post not found")
        
        if not post.can_be_viewed_by(sharer_id):
            raise ValueError("Cannot share this post")
        
        # 获取会话
        conversation = self._conversation_repo.find_by_id(
            ConversationId(conversation_id)
        )
        if not conversation:
            raise ValueError("Conversation not found")
        
        if not conversation.is_participant(sharer_id):
            raise ValueError("Not a participant of this conversation")
        
        # 发送分享消息
        content = MessageContent.trip_share_message(
            trip_id=post_id.value,
            message=message or f"分享了帖子：{post.content.title}"
        )
        conversation.send_message(sharer_id, content)
        
        # 记录分享事件
        recipient_ids = [p for p in conversation.participant_ids if p != sharer_id]
        post.share_to(sharer_id, recipient_ids)
        
        # 保存
        self._post_repo.save(post)
        self._conversation_repo.save(conversation)
    
    def share_post_to_friends(
        self,
        post_id: PostId,
        sharer_id: str,
        friend_ids: List[str]
    ) -> None:
        """分享帖子给多个好友
        
        为每个好友创建或查找会话并发送分享消息。
        """
        post = self._post_repo.find_by_id(post_id)
        if not post:
            raise ValueError("Post not found")
        
        if not post.can_be_viewed_by(sharer_id):
            raise ValueError("Cannot share this post")
        
        for friend_id in friend_ids:
            # 查找或创建会话
            conversation = self._conversation_repo.find_by_participants(
                sharer_id, friend_id
            )
            
            if not conversation:
                conversation = Conversation.create_private(sharer_id, friend_id)
            
            # 发送分享消息
            content = MessageContent.trip_share_message(
                trip_id=post_id.value,
                message=f"分享了帖子：{post.content.title}"
            )
            conversation.send_message(sharer_id, content)
            
            self._conversation_repo.save(conversation)
        
        # 记录分享事件
        post.share_to(sharer_id, friend_ids)
        self._post_repo.save(post)
    
    def get_or_create_conversation(
        self,
        initiator_id: str,
        participant_id: str
    ) -> Conversation:
        """获取或创建两人之间的私聊
        
        如果已存在私聊则返回，否则创建新的。
        """
        conversation = self._conversation_repo.find_by_participants(
            initiator_id, participant_id
        )
        
        if not conversation:
            conversation = Conversation.create_private(initiator_id, participant_id)
            self._conversation_repo.save(conversation)
        
        return conversation