"""
密码哈希器接口

由基础设施层实现，领域层仅依赖接口。
"""
from abc import ABC, abstractmethod

from app_auth.domain.value_objects.user_value_objects import Password, HashedPassword


class IPasswordHasher(ABC):
    """密码哈希接口"""
    
    @abstractmethod
    def hash(self, password: Password) -> HashedPassword:
        """将明文密码哈希化
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码
        """
        pass
    
    @abstractmethod
    def verify(self, password: Password, hashed: HashedPassword) -> bool:
        """验证密码是否匹配
        
        Args:
            password: 明文密码
            hashed: 哈希后的密码
            
        Returns:
            是否匹配
        """
        pass
