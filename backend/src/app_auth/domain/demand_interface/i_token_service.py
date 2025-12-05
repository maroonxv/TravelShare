"""
Token 服务接口

用于 JWT 等令牌的生成、验证和撤销。
由基础设施层实现。
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from app_auth.domain.value_objects.user_value_objects import UserId, UserRole


class ITokenService(ABC):
    """Token 服务接口"""
    
    @abstractmethod
    def generate_access_token(self, user_id: UserId, role: UserRole) -> str:
        """生成访问令牌
        
        Args:
            user_id: 用户ID
            role: 用户角色
            
        Returns:
            访问令牌字符串
        """
        pass
    
    @abstractmethod
    def generate_refresh_token(self, user_id: UserId) -> str:
        """生成刷新令牌
        
        Args:
            user_id: 用户ID
            
        Returns:
            刷新令牌字符串
        """
        pass
    
    @abstractmethod
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌并返回载荷
        
        Args:
            token: 令牌字符串
            
        Returns:
            令牌载荷字典，无效则返回 None
        """
        pass
    
    @abstractmethod
    def revoke_token(self, token: str) -> None:
        """撤销令牌
        
        Args:
            token: 令牌字符串
        """
        pass
    
    @abstractmethod
    def generate_email_verification_token(self, user_id: UserId, email: str) -> str:
        """生成邮箱验证令牌
        
        Args:
            user_id: 用户ID
            email: 待验证的邮箱
            
        Returns:
            验证令牌字符串
        """
        pass
    
    @abstractmethod
    def generate_password_reset_token(self, user_id: UserId) -> str:
        """生成密码重置令牌
        
        Args:
            user_id: 用户ID
            
        Returns:
            重置令牌字符串
        """
        pass
