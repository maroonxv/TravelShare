"""
消息实体 - Conversation 聚合的子实体
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Set

from app_social.domain.value_objects.social_value_objects import MessageContent


@dataclass
class Message:
    """消息实体
    
    作为 Conversation 聚合根的子实体。
    """
    
    message_id: str
    conversation_id: str
    sender_id: str
    content: MessageContent
    sent_at: datetime = field(default_factory=datetime.utcnow)
    is_deleted: bool = False
    read_by: Set[str] = field(default_factory=set)  # 已读用户ID集合
    
    @classmethod
    def create(
        cls,
        message_id: str,
        conversation_id: str,
        sender_id: str,
        content: MessageContent
    ) -> 'Message':
        """创建消息"""
        message = cls(
            message_id=message_id,
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content
        )
        # 发送者自动已读
        message.read_by.add(sender_id)
        return message
    
    def mark_read_by(self, user_id: str) -> bool:
        """标记为已读
        
        Returns:
            如果是新标记返回 True，已经标记过返回 False
        """
        if user_id in self.read_by:
            return False
        self.read_by.add(user_id)
        return True
    
    def is_read_by(self, user_id: str) -> bool:
        """检查是否已被某用户读取"""
        return user_id in self.read_by
    
    def soft_delete(self) -> None:
        """软删除"""
        self.is_deleted = True
    
    @property
    def is_text(self) -> bool:
        return self.content.message_type == "text"
    
    @property
    def is_image(self) -> bool:
        return self.content.message_type == "image"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Message):
            return False
        return self.message_id == other.message_id
    
    def __hash__(self) -> int:
        return hash(self.message_id)