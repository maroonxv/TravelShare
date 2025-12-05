"""
密码哈希器实现

使用 passlib 库实现 IPasswordHasher 接口。
"""
from passlib.hash import bcrypt

from app_auth.domain.demand_interface.i_password_hasher import IPasswordHasher
from app_auth.domain.value_objects.user_value_objects import Password, HashedPassword


class PasswordHasherImpl(IPasswordHasher):
    """密码哈希器实现 - 使用 bcrypt 算法"""
    
    def hash(self, password: Password) -> HashedPassword:
        """将明文密码哈希化
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码
        """
        hashed = bcrypt.hash(password.value)
        return HashedPassword(value=hashed)
    
    def verify(self, password: Password, hashed: HashedPassword) -> bool:
        """验证密码是否匹配
        
        Args:
            password: 明文密码
            hashed: 哈希后的密码
            
        Returns:
            是否匹配
        """
        return bcrypt.verify(password.value, hashed.value)
