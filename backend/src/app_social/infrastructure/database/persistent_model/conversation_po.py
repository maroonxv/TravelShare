"""
会话持久化对象 (PO - Persistent Object)

用于 SQLAlchemy ORM 映射，与数据库表对应。
"""
from datetime import datetime
from typing import Optional, Set, List, Dict

from sqlalchemy import Column, String, DateTime, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from shared.database.core import Base

from app_social.domain.aggregate.conversation_aggregate import Conversation
from app_social.domain.entity.message_entity import Message
from app_social.domain.value_objects.social_value_objects import (
    ConversationId, ConversationType, MessageContent, ConversationRole
)


# 会话参与者关联表
conversation_participants = Table(
    'conversation_participants',
    Base.metadata,
    Column('conversation_id', String(36), ForeignKey('conversations.id'), primary_key=True),
    Column('user_id', String(36), primary_key=True),
    Column('role', String(20), nullable=False, default='member') # owner, admin, member
)


class ConversationPO(Base):
    """会话持久化对象 - SQLAlchemy 模型"""
    
    __tablename__ = 'conversations'
    
    id = Column(String(36), primary_key=True)
    conversation_type = Column(String(20), nullable=False, default='private')
    title = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_message_at = Column(DateTime, nullable=True)
    
    # 关联 - 消息由 ConversationRepository 一起加载
    messages = relationship('MessagePO', back_populates='conversation', cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f"ConversationPO(id={self.id}, type={self.conversation_type})"
    
    def to_domain(self, participants: Dict[str, ConversationRole], messages: List['MessagePO']) -> Conversation:
        """将持久化对象转换为领域实体
        
        Args:
            participants: 参与者ID及角色映射
            messages: 消息持久化对象列表
            
        Returns:
            Conversation 领域实体
        """
        domain_messages = [msg.to_domain() for msg in messages]
        
        return Conversation.reconstitute(
            conversation_id=ConversationId(self.id),
            participants=participants,
            messages=domain_messages,
            conversation_type=ConversationType(self.conversation_type),
            created_at=self.created_at,
            last_message_at=self.last_message_at,
            title=self.title
        )
    
    @classmethod
    def from_domain(cls, conversation: Conversation) -> 'ConversationPO':
        """从领域实体创建持久化对象
        
        Args:
            conversation: Conversation 领域实体
            
        Returns:
            ConversationPO 持久化对象
        """
        return cls(
            id=conversation.id.value,
            conversation_type=conversation.conversation_type.value,
            title=conversation.title,
            created_at=conversation.created_at,
            last_message_at=conversation.last_message_at
        )
    
    def update_from_domain(self, conversation: Conversation) -> None:
        """从领域实体更新持久化对象
        
        Args:
            conversation: Conversation 领域实体
        """
        self.conversation_type = conversation.conversation_type.value
        self.title = conversation.title
        self.last_message_at = conversation.last_message_at
