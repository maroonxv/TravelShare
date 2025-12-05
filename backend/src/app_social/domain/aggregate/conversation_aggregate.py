"""
Conversation 聚合根 - 会话管理

管理私信对话，包含消息收发、已读状态等。
"""
from datetime import datetime
from typing import List, Optional, Set
import uuid

from app_social.domain.value_objects.social_value_objects import (
    ConversationId, MessageContent, ConversationType
)
from app_social.domain.entity.message_entity import Message
from app_social.domain.domain_event.social_events import (
    DomainEvent, ConversationCreatedEvent, MessageSentEvent,
    MessageDeletedEvent, MessagesReadEvent, ParticipantAddedEvent,
    ParticipantRemovedEvent
)


class Conversation:
    """会话聚合根
    
    管理私信对话和消息。
    """
    
    def __init__(
        self,
        conversation_id: ConversationId,
        participant_ids: Set[str],
        conversation_type: ConversationType = ConversationType.PRIVATE,
        created_at: Optional[datetime] = None,
        last_message_at: Optional[datetime] = None,
        title: Optional[str] = None  # 群聊标题
    ):
        if len(participant_ids) < 2:
            raise ValueError("Conversation requires at least 2 participants")
        
        self._id = conversation_id
        self._participant_ids = participant_ids
        self._conversation_type = conversation_type
        self._created_at = created_at or datetime.utcnow()
        self._last_message_at = last_message_at
        self._title = title
        self._messages: List[Message] = []
        self._domain_events: List[DomainEvent] = []
    
    # ==================== 工厂方法 ====================
    
    @classmethod
    def create_private(cls, initiator_id: str, participant_id: str) -> 'Conversation':
        """创建私聊（一对一会话）"""
        if initiator_id == participant_id:
            raise ValueError("Cannot create conversation with yourself")
        
        conv = cls(
            conversation_id=ConversationId.generate(),
            participant_ids={initiator_id, participant_id},
            conversation_type=ConversationType.PRIVATE
        )
        
        conv._add_event(ConversationCreatedEvent(
            conversation_id=conv.id.value,
            creator_id=initiator_id,
            participant_ids=tuple(conv._participant_ids),
            conversation_type="private"
        ))
        
        return conv
    
    @classmethod
    def create_group(
        cls,
        creator_id: str,
        participant_ids: List[str],
        title: Optional[str] = None
    ) -> 'Conversation':
        """创建群聊"""
        all_participants = {creator_id} | set(participant_ids)
        
        if len(all_participants) < 2:
            raise ValueError("Group chat requires at least 2 participants")
        
        conv = cls(
            conversation_id=ConversationId.generate(),
            participant_ids=all_participants,
            conversation_type=ConversationType.GROUP,
            title=title
        )
        
        conv._add_event(ConversationCreatedEvent(
            conversation_id=conv.id.value,
            creator_id=creator_id,
            participant_ids=tuple(conv._participant_ids),
            conversation_type="group"
        ))
        
        return conv
    
    @classmethod
    def reconstitute(
        cls,
        conversation_id: ConversationId,
        participant_ids: Set[str],
        messages: List[Message],
        conversation_type: ConversationType = ConversationType.PRIVATE,
        created_at: Optional[datetime] = None,
        last_message_at: Optional[datetime] = None,
        title: Optional[str] = None
    ) -> 'Conversation':
        """从持久化数据重建会话"""
        conv = cls(
            conversation_id=conversation_id,
            participant_ids=participant_ids,
            conversation_type=conversation_type,
            created_at=created_at,
            last_message_at=last_message_at,
            title=title
        )
        conv._messages = messages
        return conv
    
    # ==================== 属性访问器 ====================
    
    @property
    def id(self) -> ConversationId:
        return self._id
    
    @property
    def participant_ids(self) -> Set[str]:
        return self._participant_ids.copy()
    
    @property
    def conversation_type(self) -> ConversationType:
        return self._conversation_type
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def last_message_at(self) -> Optional[datetime]:
        return self._last_message_at
    
    @property
    def title(self) -> Optional[str]:
        return self._title
    
    @property
    def messages(self) -> List[Message]:
        return [m for m in self._messages if not m.is_deleted]
    
    @property
    def message_count(self) -> int:
        return len([m for m in self._messages if not m.is_deleted])
    
    @property
    def participant_count(self) -> int:
        return len(self._participant_ids)
    
    @property
    def is_group(self) -> bool:
        return self._conversation_type == ConversationType.GROUP
    
    # ==================== 消息管理 ====================
    
    def send_message(self, sender_id: str, content: MessageContent) -> Message:
        """发送消息
        
        Args:
            sender_id: 发送者ID
            content: 消息内容
            
        Returns:
            创建的消息实体
        """
        if sender_id not in self._participant_ids:
            raise ValueError("Sender is not a participant of this conversation")
        
        message = Message.create(
            message_id=str(uuid.uuid4()),
            conversation_id=self._id.value,
            sender_id=sender_id,
            content=content
        )
        
        self._messages.append(message)
        self._last_message_at = message.sent_at
        
        # 通知其他参与者
        recipient_ids = [p for p in self._participant_ids if p != sender_id]
        self._add_event(MessageSentEvent(
            conversation_id=self._id.value,
            message_id=message.message_id,
            sender_id=sender_id,
            recipient_ids=tuple(recipient_ids),
            message_type=content.message_type
        ))
        
        return message
    
    def delete_message(self, message_id: str, deleted_by: str) -> None:
        """删除消息（软删除）
        
        仅发送者可以删除自己的消息。
        """
        message = self._find_message(message_id)
        if not message:
            raise ValueError("Message not found")
        
        if message.sender_id != deleted_by:
            raise ValueError("Only sender can delete the message")
        
        message.soft_delete()
        
        self._add_event(MessageDeletedEvent(
            conversation_id=self._id.value,
            message_id=message_id,
            deleted_by=deleted_by
        ))
    
    def mark_as_read(self, user_id: str, up_to_message_id: Optional[str] = None) -> int:
        """标记消息为已读
        
        Args:
            user_id: 用户ID
            up_to_message_id: 读到哪条消息ID（可选，不指定则标记全部）
            
        Returns:
            标记为已读的消息数量
        """
        if user_id not in self._participant_ids:
            raise ValueError("User is not a participant")
        
        count = 0
        for message in self._messages:
            if message.is_deleted:
                continue
            if message.mark_read_by(user_id):
                count += 1
            if up_to_message_id and message.message_id == up_to_message_id:
                break
        
        if count > 0:
            self._add_event(MessagesReadEvent(
                conversation_id=self._id.value,
                user_id=user_id,
                up_to_message_id=up_to_message_id or (self._messages[-1].message_id if self._messages else "")
            ))
        
        return count
    
    def get_unread_count(self, user_id: str) -> int:
        """获取未读消息数量"""
        if user_id not in self._participant_ids:
            return 0
        
        count = 0
        for message in self._messages:
            if not message.is_deleted and not message.is_read_by(user_id):
                count += 1
        return count
    
    def get_recent_messages(self, limit: int = 50) -> List[Message]:
        """获取最近的消息"""
        valid_messages = [m for m in self._messages if not m.is_deleted]
        return valid_messages[-limit:]
    
    def _find_message(self, message_id: str) -> Optional[Message]:
        """查找消息"""
        for message in self._messages:
            if message.message_id == message_id:
                return message
        return None
    
    # ==================== 参与者管理（仅群聊） ====================
    
    def add_participant(self, user_id: str, added_by: str) -> None:
        """添加参与者
        
        仅群聊可以添加新参与者。
        """
        if not self.is_group:
            raise ValueError("Cannot add participants to private conversation")
        
        if added_by not in self._participant_ids:
            raise ValueError("Only participants can add new members")
        
        if user_id in self._participant_ids:
            return  # 已是参与者
        
        self._participant_ids.add(user_id)
        
        self._add_event(ParticipantAddedEvent(
            conversation_id=self._id.value,
            user_id=user_id,
            added_by=added_by
        ))
    
    def remove_participant(self, user_id: str, removed_by: str) -> None:
        """移除参与者
        
        仅群聊可以移除参与者，且只能自己退出或被群主移除。
        """
        if not self.is_group:
            raise ValueError("Cannot remove participants from private conversation")
        
        if user_id not in self._participant_ids:
            raise ValueError("User is not a participant")
        
        # 目前简化处理：只能自己退出
        if user_id != removed_by:
            raise ValueError("Can only remove yourself from the group")
        
        if len(self._participant_ids) <= 2:
            raise ValueError("Cannot have less than 2 participants")
        
        self._participant_ids.remove(user_id)
        
        self._add_event(ParticipantRemovedEvent(
            conversation_id=self._id.value,
            user_id=user_id,
            removed_by=removed_by
        ))
    
    def update_title(self, new_title: str, updated_by: str) -> None:
        """更新群聊标题"""
        if not self.is_group:
            raise ValueError("Cannot set title for private conversation")
        
        if updated_by not in self._participant_ids:
            raise ValueError("Only participants can update title")
        
        self._title = new_title
    
    # ==================== 查询方法 ====================
    
    def is_participant(self, user_id: str) -> bool:
        """检查是否为参与者"""
        return user_id in self._participant_ids
    
    def get_other_participant(self, user_id: str) -> Optional[str]:
        """获取私聊中的另一方（仅私聊有效）"""
        if self.is_group or user_id not in self._participant_ids:
            return None
        
        for p in self._participant_ids:
            if p != user_id:
                return p
        return None
    
    # ==================== 事件管理 ====================
    
    def _add_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)
    
    def pop_events(self) -> List[DomainEvent]:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Conversation):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id.value)
    
    def __repr__(self) -> str:
        return f"Conversation(id={self._id.value}, type={self._conversation_type.value}, participants={len(self._participant_ids)})"