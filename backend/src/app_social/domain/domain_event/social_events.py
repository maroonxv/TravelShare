"""
app_social 领域事件定义
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Tuple
import uuid
from shared.domain_event import DomainEvent


# ==================== 帖子相关事件 ====================

@dataclass(frozen=True)
class PostCreatedEvent(DomainEvent):
    """帖子创建事件"""
    post_id: str = ""
    author_id: str = ""
    title: str = ""
    visibility: str = "public"
    trip_id: Optional[str] = None  # 关联的旅行ID（游记）


@dataclass(frozen=True)
class PostUpdatedEvent(DomainEvent):
    """帖子更新事件"""
    post_id: str = ""
    author_id: str = ""
    updated_fields: Tuple[str, ...] = ()


@dataclass(frozen=True)
class PostDeletedEvent(DomainEvent):
    """帖子删除事件"""
    post_id: str = ""
    author_id: str = ""


@dataclass(frozen=True)
class PostVisibilityChangedEvent(DomainEvent):
    """帖子可见性变更事件"""
    post_id: str = ""
    old_visibility: str = ""
    new_visibility: str = ""


# ==================== 评论相关事件 ====================

@dataclass(frozen=True)
class CommentAddedEvent(DomainEvent):
    """评论添加事件 - 通知帖子作者"""
    post_id: str = ""
    comment_id: str = ""
    author_id: str = ""  # 评论者ID
    post_author_id: str = ""  # 帖子作者ID
    parent_comment_id: Optional[str] = None  # 回复的评论ID


@dataclass(frozen=True)
class CommentRemovedEvent(DomainEvent):
    """评论删除事件"""
    post_id: str = ""
    comment_id: str = ""
    removed_by: str = ""


# ==================== 点赞相关事件 ====================

@dataclass(frozen=True)
class PostLikedEvent(DomainEvent):
    """点赞事件 - 通知帖子作者"""
    post_id: str = ""
    user_id: str = ""
    post_author_id: str = ""


@dataclass(frozen=True)
class PostUnlikedEvent(DomainEvent):
    """取消点赞事件"""
    post_id: str = ""
    user_id: str = ""


# ==================== 分享相关事件 ====================

@dataclass(frozen=True)
class PostSharedEvent(DomainEvent):
    """帖子分享事件"""
    post_id: str = ""
    sharer_id: str = ""
    shared_to_ids: Tuple[str, ...] = ()  # 分享给的用户ID列表


# ==================== 会话相关事件 ====================

@dataclass(frozen=True)
class ConversationCreatedEvent(DomainEvent):
    """会话创建事件"""
    conversation_id: str = ""
    creator_id: str = ""
    participant_ids: Tuple[str, ...] = ()
    conversation_type: str = "private"  # private or group


@dataclass(frozen=True)
class ParticipantAddedEvent(DomainEvent):
    """参与者添加事件"""
    conversation_id: str = ""
    user_id: str = ""
    added_by: str = ""


@dataclass(frozen=True)
class ParticipantRemovedEvent(DomainEvent):
    """参与者移除事件"""
    conversation_id: str = ""
    user_id: str = ""
    removed_by: str = ""


# ==================== 消息相关事件 ====================

@dataclass(frozen=True)
class MessageSentEvent(DomainEvent):
    """消息发送事件 - 通知接收者"""
    conversation_id: str = ""
    message_id: str = ""
    sender_id: str = ""
    recipient_ids: Tuple[str, ...] = ()  # 接收者ID列表
    message_type: str = "text"
    content: str = ""
    media_url: Optional[str] = None
    reference_id: Optional[str] = None


@dataclass(frozen=True)
class MessageDeletedEvent(DomainEvent):
    """消息删除事件"""
    conversation_id: str = ""
    message_id: str = ""
    deleted_by: str = ""


@dataclass(frozen=True)
class MessagesReadEvent(DomainEvent):
    """消息已读事件"""
    conversation_id: str = ""
    user_id: str = ""
    up_to_message_id: str = ""  # 读到哪条消息
