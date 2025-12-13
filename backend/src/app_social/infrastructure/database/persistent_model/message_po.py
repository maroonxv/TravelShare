"""
消息持久化对象 (PO - Persistent Object)

用于 SQLAlchemy ORM 映射，与数据库表对应。
"""
from datetime import datetime
from typing import Optional, Set
import json

from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from shared.database.core import Base

from app_social.domain.entity.message_entity import Message
from app_social.domain.value_objects.social_value_objects import MessageContent


class MessagePO(Base):
    """消息持久化对象 - SQLAlchemy 模型"""
    
    __tablename__ = 'messages'
    
    id = Column(String(36), primary_key=True)
    conversation_id = Column(String(36), ForeignKey('conversations.id'), nullable=False, index=True)
    sender_id = Column(String(36), nullable=False, index=True)
    
    # 消息内容
    content_text = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False, default='text')
    media_url = Column(String(500), nullable=True)
    reference_id = Column(String(36), nullable=True)
    
    # 状态
    sent_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_deleted = Column(Boolean, nullable=False, default=False)
    read_by_json = Column(Text, nullable=False, default='[]')  # JSON 格式存储已读用户ID列表
    
    # 关联
    conversation = relationship('ConversationPO', back_populates='messages')
    
    def __repr__(self) -> str:
        return f"MessagePO(id={self.id}, sender={self.sender_id})"
    
    @property
    def read_by(self) -> Set[str]:
        """获取已读用户ID集合"""
        return set(json.loads(self.read_by_json))
    
    @read_by.setter
    def read_by(self, value: Set[str]) -> None:
        """设置已读用户ID集合"""
        self.read_by_json = json.dumps(list(value))
    
    def to_domain(self) -> Message:
        """将持久化对象转换为领域实体
        
        Returns:
            Message 领域实体
        """
        content = MessageContent(
            text=self.content_text,
            message_type=self.message_type,
            media_url=self.media_url,
            reference_id=self.reference_id
        )
        
        message = Message(
            message_id=self.id,
            conversation_id=self.conversation_id,
            sender_id=self.sender_id,
            content=content,
            sent_at=self.sent_at,
            is_deleted=self.is_deleted,
            read_by=self.read_by
        )
        
        return message
    
    @classmethod
    def from_domain(cls, message: Message) -> 'MessagePO':
        """从领域实体创建持久化对象
        
        Args:
            message: Message 领域实体
            
        Returns:
            MessagePO 持久化对象
        """
        po = cls(
            id=message.message_id,
            conversation_id=message.conversation_id,
            sender_id=message.sender_id,
            content_text=message.content.text,
            message_type=message.content.message_type,
            media_url=message.content.media_url,
            reference_id=message.content.reference_id,
            sent_at=message.sent_at,
            is_deleted=message.is_deleted
        )
        po.read_by = message.read_by
        return po
    
    def update_from_domain(self, message: Message) -> None:
        """从领域实体更新持久化对象
        
        Args:
            message: Message 领域实体
        """
        self.content_text = message.content.text
        self.message_type = message.content.message_type
        self.media_url = message.content.media_url
        self.reference_id = message.content.reference_id
        self.is_deleted = message.is_deleted
        self.read_by = message.read_by
