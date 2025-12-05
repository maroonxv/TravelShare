"""
app_auth 领域事件定义

领域事件特征：
1. 不可变 (frozen=True)
2. 记录已发生的业务事实
3. 包含事件ID和发生时间
4. 用于限界上下文内部和跨上下文通信
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Tuple
import uuid


@dataclass(frozen=True)
class DomainEvent:
    """领域事件基类"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def event_type(self) -> str:
        """返回事件类型名称"""
        return self.__class__.__name__


@dataclass(frozen=True)
class UserRegisteredEvent(DomainEvent):
    """用户注册事件
    
    跨上下文事件：通知 app_travel 和 app_social 创建用户档案
    """
    user_id: str = ""
    username: str = ""
    email: str = ""
    role: str = ""


@dataclass(frozen=True)
class UserLoggedInEvent(DomainEvent):
    """用户登录事件"""
    user_id: str = ""
    login_ip: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass(frozen=True)
class UserLoggedOutEvent(DomainEvent):
    """用户登出事件"""
    user_id: str = ""


@dataclass(frozen=True)
class UserPasswordChangedEvent(DomainEvent):
    """密码更改事件"""
    user_id: str = ""


@dataclass(frozen=True)
class UserProfileUpdatedEvent(DomainEvent):
    """用户资料更新事件"""
    user_id: str = ""
    updated_fields: Tuple[str, ...] = ()  # 更新的字段名列表


@dataclass(frozen=True)
class UserDeactivatedEvent(DomainEvent):
    """账户停用事件
    
    跨上下文事件：通知其他上下文处理用户停用
    """
    user_id: str = ""
    reason: Optional[str] = None


@dataclass(frozen=True)
class UserReactivatedEvent(DomainEvent):
    """账户重新激活事件"""
    user_id: str = ""


@dataclass(frozen=True)
class UserEmailVerifiedEvent(DomainEvent):
    """邮箱验证完成事件"""
    user_id: str = ""
    email: str = ""


@dataclass(frozen=True)
class PasswordResetRequestedEvent(DomainEvent):
    """密码重置请求事件"""
    user_id: str = ""
    email: str = ""
    reset_token: str = ""


@dataclass(frozen=True)
class PasswordResetCompletedEvent(DomainEvent):
    """密码重置完成事件"""
    user_id: str = ""