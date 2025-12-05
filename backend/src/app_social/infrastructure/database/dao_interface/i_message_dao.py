"""
消息 DAO 接口

定义消息持久化对象的数据访问操作。
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app_social.infrastructure.database.persistent_model.message_po import MessagePO


class IMessageDao(ABC):
    """消息数据访问对象接口"""
    
    @abstractmethod
    def find_by_id(self, message_id: str) -> Optional[MessagePO]:
        """根据ID查找消息
        
        Args:
            message_id: 消息ID
            
        Returns:
            消息持久化对象，不存在则返回 None
        """
        pass
    
    @abstractmethod
    def find_by_conversation(
        self, 
        conversation_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[MessagePO]:
        """获取会话中的消息列表
        
        Args:
            conversation_id: 会话ID
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            消息持久化对象列表，按发送时间排序
        """
        pass
    
    @abstractmethod
    def add(self, message_po: MessagePO) -> None:
        """添加消息
        
        Args:
            message_po: 消息持久化对象
        """
        pass
    
    @abstractmethod
    def update(self, message_po: MessagePO) -> None:
        """更新消息
        
        Args:
            message_po: 消息持久化对象
        """
        pass
    
    @abstractmethod
    def delete(self, message_id: str) -> None:
        """删除消息
        
        Args:
            message_id: 消息ID
        """
        pass
    
    @abstractmethod
    def delete_by_conversation(self, conversation_id: str) -> None:
        """删除会话中的所有消息
        
        Args:
            conversation_id: 会话ID
        """
        pass
    
    @abstractmethod
    def mark_read(self, message_id: str, user_id: str) -> None:
        """标记消息为已读
        
        Args:
            message_id: 消息ID
            user_id: 用户ID
        """
        pass
    
    @abstractmethod
    def mark_all_read(self, conversation_id: str, user_id: str) -> int:
        """标记会话中所有消息为已读
        
        Args:
            conversation_id: 会话ID
            user_id: 用户ID
            
        Returns:
            标记为已读的消息数量
        """
        pass
