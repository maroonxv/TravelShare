"""
会话仓库实现

实现 IConversationRepository 接口，包含消息管理（遵循 DDD 一个聚合根一个仓库原则）。
负责 Conversation 聚合根及其子实体 Message 的持久化。
"""
from typing import List, Optional, Set, Dict

from app_social.domain.demand_interface.i_conversation_repository import IConversationRepository
from app_social.domain.aggregate.conversation_aggregate import Conversation
from app_social.domain.entity.message_entity import Message
from app_social.domain.value_objects.social_value_objects import ConversationId, ConversationRole
from app_social.infrastructure.database.dao_interface.i_conversation_dao import IConversationDao
from app_social.infrastructure.database.dao_interface.i_message_dao import IMessageDao
from app_social.infrastructure.database.persistent_model.conversation_po import ConversationPO
from app_social.infrastructure.database.persistent_model.message_po import MessagePO


class ConversationRepositoryImpl(IConversationRepository):
    """会话仓库实现
    
    同时管理会话和消息的持久化，因为 Message 是 Conversation 聚合的子实体。
    """
    
    def __init__(self, conversation_dao: IConversationDao, message_dao: IMessageDao):
        """初始化仓库
        
        Args:
            conversation_dao: 会话数据访问对象
            message_dao: 消息数据访问对象
        """
        self._conversation_dao = conversation_dao
        self._message_dao = message_dao
    
    def save(self, conversation: Conversation) -> None:
        """保存会话（新增或更新）
        
        同时保存会话中的新消息。
        """
        existing_po = self._conversation_dao.find_by_id(conversation.id.value)
        
        if existing_po:
            # 更新现有会话
            existing_po.update_from_domain(conversation)
            self._conversation_dao.update(existing_po)
        else:
            # 添加新会话
            conversation_po = ConversationPO.from_domain(conversation)
            self._conversation_dao.add(conversation_po)
        
        # 保存/更新消息
        self._save_messages(conversation)
        
        # 保存参与者
        participants_data = []
        for uid, role in conversation.participants_with_roles.items():
            participants_data.append({
                "user_id": uid,
                "role": role.value
            })
            
        self._conversation_dao.update_participants(
            conversation.id.value, 
            participants_data
        )
    
    def _save_messages(self, conversation: Conversation) -> None:
        """保存会话中的消息
        
        Args:
            conversation: 会话聚合根
        """
        for message in conversation.messages:
            existing_msg = self._message_dao.find_by_id(message.message_id)
            if existing_msg:
                existing_msg.update_from_domain(message)
                self._message_dao.update(existing_msg)
            else:
                message_po = MessagePO.from_domain(message)
                self._message_dao.add(message_po)
    
    def find_by_id(self, conversation_id: ConversationId) -> Optional[Conversation]:
        """根据ID查找会话"""
        conversation_po = self._conversation_dao.find_by_id(conversation_id.value)
        if not conversation_po:
            return None
        
        # 加载消息
        message_pos = self._message_dao.find_by_conversation(conversation_id.value)
        
        # 加载参与者和角色
        participants = self._load_participants(conversation_id.value)
        
        return conversation_po.to_domain(participants, message_pos)
    
    def find_by_participants(self, user_id1: str, user_id2: str) -> Optional[Conversation]:
        """查找两人之间的私聊"""
        conversation_po = self._conversation_dao.find_by_participants(user_id1, user_id2)
        if not conversation_po:
            return None
        
        message_pos = self._message_dao.find_by_conversation(conversation_po.id)
        
        # 加载参与者和角色
        participants = self._load_participants(conversation_po.id)
        
        return conversation_po.to_domain(participants, message_pos)
    
    def find_by_user(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Conversation]:
        """获取用户参与的所有会话"""
        conversation_pos = self._conversation_dao.find_by_user(user_id, limit, offset)
        
        conversations = []
        for po in conversation_pos:
            message_pos = self._message_dao.find_by_conversation(po.id, limit=50)
            participants = self._load_participants(po.id)
            conversations.append(po.to_domain(participants, message_pos))
        
        return conversations
    
    def find_by_user_with_unread(self, user_id: str) -> List[Conversation]:
        """获取用户有未读消息的会话"""
        conversation_pos = self._conversation_dao.find_by_user_with_unread(user_id)
        
        conversations = []
        for po in conversation_pos:
            message_pos = self._message_dao.find_by_conversation(po.id, limit=50)
            participants = self._load_participants(po.id)
            conversations.append(po.to_domain(participants, message_pos))
        
        return conversations
    
    def delete(self, conversation_id: ConversationId) -> None:
        """删除会话及其所有消息"""
        self._message_dao.delete_by_conversation(conversation_id.value)
        self._conversation_dao.delete(conversation_id.value)
    
    def exists(self, conversation_id: ConversationId) -> bool:
        """检查会话是否存在"""
        return self._conversation_dao.exists(conversation_id.value)
    
    def _load_participants(self, conversation_id: str) -> Dict[str, ConversationRole]:
        """加载会话参与者及角色"""
        rows = self._conversation_dao.get_participants_with_roles(conversation_id)
        result = {}
        for row in rows:
            try:
                role = ConversationRole(row["role"])
            except ValueError:
                role = ConversationRole.MEMBER # 默认回退
            result[row["user_id"]] = role
        return result
