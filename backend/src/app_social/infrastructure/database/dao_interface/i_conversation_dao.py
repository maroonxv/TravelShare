"""
会话 DAO 接口

定义会话持久化对象的数据访问操作。
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from app_social.infrastructure.database.persistent_model.conversation_po import ConversationPO


class IConversationDao(ABC):
    """会话数据访问对象接口"""
    
    @abstractmethod
    def find_by_id(self, conversation_id: str) -> Optional[ConversationPO]:
        """根据ID查找会话
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            会话持久化对象，不存在则返回 None
        """
        pass
    
    @abstractmethod
    def find_by_participants(self, user_id1: str, user_id2: str) -> Optional[ConversationPO]:
        """查找两人之间的私聊
        
        Args:
            user_id1: 用户1的ID
            user_id2: 用户2的ID
            
        Returns:
            会话持久化对象，不存在则返回 None
        """
        pass
    
    @abstractmethod
    def find_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[ConversationPO]:
        """获取用户参与的所有会话
        
        Args:
            user_id: 用户ID
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            会话持久化对象列表，按最后消息时间倒序
        """
        pass
    
    @abstractmethod
    def find_by_user_with_unread(self, user_id: str) -> List[ConversationPO]:
        """获取用户有未读消息的会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            有未读消息的会话列表
        """
        pass
    
    @abstractmethod
    def add(self, conversation_po: ConversationPO) -> None:
        """添加会话
        
        Args:
            conversation_po: 会话持久化对象
        """
        pass
    
    @abstractmethod
    def update(self, conversation_po: ConversationPO) -> None:
        """更新会话
        
        Args:
            conversation_po: 会话持久化对象
        """
        pass
    
    @abstractmethod
    def delete(self, conversation_id: str) -> None:
        """删除会话
        
        Args:
            conversation_id: 会话ID
        """
        pass
    
    @abstractmethod
    def exists(self, conversation_id: str) -> bool:
        """检查会话是否存在
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            是否存在
        """
        pass

    @abstractmethod
    def get_participants_with_roles(self, conversation_id: str) -> List[Dict[str, str]]:
        """获取会话参与者及角色
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            参与者列表 [{"user_id": "...", "role": "..."}]
        """
        pass

    @abstractmethod
    def update_participants(self, conversation_id: str, participants: List[Dict[str, str]]) -> None:
        """更新会话参与者
        
        Args:
            conversation_id: 会话ID
            participants: 参与者列表 [{"user_id": "...", "role": "..."}]
        """
        pass
