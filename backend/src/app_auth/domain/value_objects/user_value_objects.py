"""
app_auth 值对象定义

值对象特征：
1. 不可变 (frozen=True)
2. 包含验证逻辑
3. 通过值相等判断
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid
import re


@dataclass(frozen=True)
class UserId:
    """用户唯一标识"""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("UserId cannot be empty")
    
    @classmethod
    def generate(cls) -> 'UserId':
        """生成新的用户ID"""
        return cls(str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Email:
    """邮箱地址值对象"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Email cannot be empty")
        # 简单的邮箱格式验证
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, self.value):
            raise ValueError(f"Invalid email format: {self.value}")
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def domain(self) -> str:
        """获取邮箱域名"""
        return self.value.split('@')[1]


@dataclass(frozen=True)
class Username:
    """用户名值对象"""
    value: str
    
    MIN_LENGTH = 2
    MAX_LENGTH = 50
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Username cannot be empty")
        if len(self.value) < self.MIN_LENGTH:
            raise ValueError(f"Username must be at least {self.MIN_LENGTH} characters")
        if len(self.value) > self.MAX_LENGTH:
            raise ValueError(f"Username must be at most {self.MAX_LENGTH} characters")
        # 只允许字母、数字、下划线
        if not re.match(r'^[\w\u4e00-\u9fa5]+$', self.value):
            raise ValueError("Username can only contain letters, numbers, underscores, and Chinese characters")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Password:
    """明文密码值对象 - 仅用于创建/验证，不持久化"""
    value: str
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Password cannot be empty")
        if len(self.value) < self.MIN_LENGTH:
            raise ValueError(f"Password must be at least {self.MIN_LENGTH} characters")
        if len(self.value) > self.MAX_LENGTH:
            raise ValueError(f"Password must be at most {self.MAX_LENGTH} characters")
    
    def __str__(self) -> str:
        # 安全起见，不暴露密码内容
        return "********"


@dataclass(frozen=True)
class HashedPassword:
    """哈希后的密码值对象 - 用于持久化"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("HashedPassword cannot be empty")
    
    def __str__(self) -> str:
        return "********"


class UserRole(Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    
    @classmethod
    def from_string(cls, role_str: str) -> 'UserRole':
        """从字符串创建角色"""
        role_str = role_str.lower()
        for role in cls:
            if role.value == role_str:
                return role
        raise ValueError(f"Unknown role: {role_str}")


@dataclass(frozen=True)
class UserProfile:
    """用户资料值对象"""
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    
    def __post_init__(self):
        if self.bio and len(self.bio) > 500:
            raise ValueError("Bio must be at most 500 characters")
        if self.location and len(self.location) > 100:
            raise ValueError("Location must be at most 100 characters")