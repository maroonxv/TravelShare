"""
会话仓库接口
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app_social.domain.aggregate.conversation_aggregate import Conversation
from app_social.domain.value_objects.social_value_objects import ConversationId


class IConversationRepository(ABC):
    """会话仓库接口"""
    
    @abstractmethod
    def save(self, conversation: Conversation) -> None:
        """保存会话（新增或更新）"""
        pass
    
    @abstractmethod
    def find_by_id(self, conversation_id: ConversationId) -> Optional[Conversation]:
        """根据ID查找会话"""
        pass
    
    @abstractmethod
    def find_by_participants(self, user_id1: str, user_id2: str) -> Optional[Conversation]:
        """查找两人之间的私聊
        
        Args:
            user_id1: 用户1的ID
            user_id2: 用户2的ID
            
        Returns:
            如果存在私聊则返回会话，否则返回 None
        """
        pass
    
    @abstractmethod
    def find_by_user(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Conversation]:
        """获取用户参与的所有会话
        
        按最后消息时间倒序排列。
        """
        pass
    
    @abstractmethod
    def find_by_user_with_unread(self, user_id: str) -> List[Conversation]:
        """获取用户有未读消息的会话"""
        pass
    
    @abstractmethod
    def delete(self, conversation_id: ConversationId) -> None:
        """删除会话"""
        pass
    
    @abstractmethod
    def exists(self, conversation_id: ConversationId) -> bool:
        """检查会话是否存在"""
        pass
