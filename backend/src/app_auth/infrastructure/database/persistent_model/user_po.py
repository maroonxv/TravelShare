"""
用户持久化对象 (PO - Persistent Object)

用于 SQLAlchemy ORM 映射，与数据库表对应。
包含与 Domain Entity 的双向转换方法。
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, Text
from shared.database.core import Base

from app_auth.domain.entity.user_entity import User
from app_auth.domain.value_objects.user_value_objects import (
    UserId, Email, Username, HashedPassword, UserRole, UserProfile
)


class UserPO(Base):
    """用户持久化对象 - SQLAlchemy 模型"""
    
    __tablename__ = 'users'
    
    # 主键和唯一字段
    id = Column(String(36), primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # 用户角色
    role = Column(String(20), nullable=False, default='user')
    
    # 用户资料
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    
    # 状态字段
    is_active = Column(Boolean, nullable=False, default=True)
    is_email_verified = Column(Boolean, nullable=False, default=False)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"UserPO(id={self.id}, username={self.username}, email={self.email})"
    
    def to_domain(self) -> User:
        """将持久化对象转换为领域实体
        
        Returns:
            User 领域实体
        """
        profile = UserProfile(
            avatar_url=self.avatar_url,
            bio=self.bio,
            location=self.location
        )
        
        return User.reconstitute(
            user_id=UserId(self.id),
            username=Username(self.username),
            email=Email(self.email),
            hashed_password=HashedPassword(self.hashed_password),
            role=UserRole.from_string(self.role),
            profile=profile,
            created_at=self.created_at,
            updated_at=self.updated_at,
            is_active=self.is_active,
            is_email_verified=self.is_email_verified
        )
    
    @classmethod
    def from_domain(cls, user: User) -> 'UserPO':
        """从领域实体创建持久化对象
        
        Args:
            user: User 领域实体
            
        Returns:
            UserPO 持久化对象
        """
        return cls(
            id=user.id.value,
            username=user.username.value,
            email=user.email.value,
            hashed_password=user.hashed_password.value,
            role=user.role.value,
            avatar_url=user.profile.avatar_url,
            bio=user.profile.bio,
            location=user.profile.location,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    def update_from_domain(self, user: User) -> None:
        """从领域实体更新持久化对象
        
        Args:
            user: User 领域实体
        """
        self.username = user.username.value
        self.email = user.email.value
        self.hashed_password = user.hashed_password.value
        self.role = user.role.value
        self.avatar_url = user.profile.avatar_url
        self.bio = user.profile.bio
        self.location = user.profile.location
        self.is_active = user.is_active
        self.is_email_verified = user.is_email_verified
        self.updated_at = user.updated_at