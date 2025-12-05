"""
用户唯一性检查器接口

用于在创建用户前检查用户名和邮箱的唯一性。
这是一个辅助接口，可以由 Repository 实现，也可以单独实现。
"""
from abc import ABC, abstractmethod

from app_auth.domain.value_objects.user_value_objects import Email, Username


class IUserUniquenessChecker(ABC):
    """用户唯一性检查接口"""
    
    @abstractmethod
    def is_email_unique(self, email: Email) -> bool:
        """检查邮箱是否唯一
        
        Args:
            email: 待检查的邮箱
            
        Returns:
            如果邮箱未被使用返回 True
        """
        pass
    
    @abstractmethod
    def is_username_unique(self, username: Username) -> bool:
        """检查用户名是否唯一
        
        Args:
            username: 待检查的用户名
            
        Returns:
            如果用户名未被使用返回 True
        """
        pass