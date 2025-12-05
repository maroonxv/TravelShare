"""
User 聚合根 - 充血模型

聚合根职责：
1. 封装所有用户相关的业务逻辑
2. 维护不变量和业务规则
3. 发布领域事件
4. 通过工厂方法创建实例
"""
from datetime import datetime
from typing import List, Optional

from app_auth.domain.value_objects.user_value_objects import (
    UserId, Email, Username, Password, HashedPassword, UserRole, UserProfile
)
from app_auth.domain.domain_event.user_events import (
    DomainEvent, UserRegisteredEvent, UserLoggedInEvent, UserLoggedOutEvent,
    UserPasswordChangedEvent, UserProfileUpdatedEvent, UserDeactivatedEvent,
    UserReactivatedEvent
)
from app_auth.domain.demand_interface.i_password_hasher import IPasswordHasher


class User:
    """用户聚合根 - 充血模型
    
    包含用户的所有业务逻辑，不只是数据容器。
    所有状态变更都通过业务方法进行，并发布相应的领域事件。
    """
    
    def __init__(
        self,
        user_id: UserId,
        username: Username,
        email: Email,
        hashed_password: HashedPassword,
        role: UserRole = UserRole.USER,
        profile: Optional[UserProfile] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_active: bool = True,
        is_email_verified: bool = False
    ):
        self._id = user_id
        self._username = username
        self._email = email
        self._hashed_password = hashed_password
        self._role = role
        self._profile = profile or UserProfile()
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or self._created_at
        self._is_active = is_active
        self._is_email_verified = is_email_verified
        self._domain_events: List[DomainEvent] = []
    
    # ==================== 工厂方法 ====================
    
    @classmethod
    def register(
        cls,
        username: Username,
        email: Email,
        password: Password,
        password_hasher: IPasswordHasher,
        role: UserRole = UserRole.USER
    ) -> 'User':
        """注册新用户的工厂方法
        
        Args:
            username: 用户名
            email: 邮箱
            password: 明文密码（将被哈希）
            password_hasher: 密码哈希器
            role: 用户角色，默认为普通用户
            
        Returns:
            新创建的 User 实例
        """
        user = cls(
            user_id=UserId.generate(),
            username=username,
            email=email,
            hashed_password=password_hasher.hash(password),
            role=role
        )
        
        # 发布用户注册事件
        user._add_event(UserRegisteredEvent(
            user_id=user.id.value,
            username=user.username.value,
            email=user.email.value,
            role=user.role.value
        ))
        
        return user
    
    @classmethod
    def reconstitute(
        cls,
        user_id: UserId,
        username: Username,
        email: Email,
        hashed_password: HashedPassword,
        role: UserRole,
        profile: Optional[UserProfile] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_active: bool = True,
        is_email_verified: bool = False
    ) -> 'User':
        """从持久化数据重建用户（不发布事件）
        
        用于 Repository 从数据库加载用户时使用。
        """
        return cls(
            user_id=user_id,
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
            profile=profile,
            created_at=created_at,
            updated_at=updated_at,
            is_active=is_active,
            is_email_verified=is_email_verified
        )
    
    # ==================== 属性访问器 ====================
    
    @property
    def id(self) -> UserId:
        return self._id
    
    @property
    def username(self) -> Username:
        return self._username
    
    @property
    def email(self) -> Email:
        return self._email
    
    @property
    def role(self) -> UserRole:
        return self._role
    
    @property
    def profile(self) -> UserProfile:
        return self._profile
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @property
    def is_email_verified(self) -> bool:
        return self._is_email_verified
    
    @property
    def hashed_password(self) -> HashedPassword:
        """仅供 Repository 持久化使用"""
        return self._hashed_password
    
    # ==================== 业务方法 ====================
    
    def authenticate(self, password: Password, password_hasher: IPasswordHasher) -> bool:
        """验证密码
        
        Args:
            password: 待验证的明文密码
            password_hasher: 密码哈希器
            
        Returns:
            密码是否正确
            
        Raises:
            ValueError: 如果账户已停用
        """
        if not self._is_active:
            raise ValueError("Account is deactivated")
        
        return password_hasher.verify(password, self._hashed_password)
    
    def record_login(self, login_ip: Optional[str] = None, user_agent: Optional[str] = None) -> None:
        """记录登录事件
        
        在认证成功后调用，发布登录事件。
        """
        self._add_event(UserLoggedInEvent(
            user_id=self._id.value,
            login_ip=login_ip,
            user_agent=user_agent
        ))
    
    def record_logout(self) -> None:
        """记录登出事件"""
        self._add_event(UserLoggedOutEvent(user_id=self._id.value))
    
    def change_password(
        self,
        old_password: Password,
        new_password: Password,
        password_hasher: IPasswordHasher
    ) -> None:
        """更改密码
        
        Args:
            old_password: 旧密码
            new_password: 新密码
            password_hasher: 密码哈希器
            
        Raises:
            ValueError: 旧密码不正确或新旧密码相同
        """
        if not password_hasher.verify(old_password, self._hashed_password):
            raise ValueError("Old password is incorrect")
        
        if old_password.value == new_password.value:
            raise ValueError("New password cannot be the same as the old password")
        
        self._hashed_password = password_hasher.hash(new_password)
        self._updated_at = datetime.utcnow()
        
        self._add_event(UserPasswordChangedEvent(user_id=self._id.value))
    
    def reset_password(self, new_password: Password, password_hasher: IPasswordHasher) -> None:
        """重置密码（忘记密码流程）
        
        不需要验证旧密码，由应用层通过令牌验证身份。
        """
        self._hashed_password = password_hasher.hash(new_password)
        self._updated_at = datetime.utcnow()
        
        self._add_event(UserPasswordChangedEvent(user_id=self._id.value))
    
    def update_username(self, new_username: Username) -> None:
        """更新用户名"""
        if self._username == new_username:
            return  # 无变化，不需要更新
        
        self._username = new_username
        self._updated_at = datetime.utcnow()
        
        self._add_event(UserProfileUpdatedEvent(
            user_id=self._id.value,
            updated_fields=('username',)
        ))
    
    def update_email(self, new_email: Email) -> None:
        """更新邮箱（需要重新验证）"""
        if self._email == new_email:
            return
        
        self._email = new_email
        self._is_email_verified = False  # 新邮箱需要重新验证
        self._updated_at = datetime.utcnow()
        
        self._add_event(UserProfileUpdatedEvent(
            user_id=self._id.value,
            updated_fields=('email',)
        ))
    
    def update_profile(self, new_profile: UserProfile) -> None:
        """更新用户资料"""
        self._profile = new_profile
        self._updated_at = datetime.utcnow()
        
        self._add_event(UserProfileUpdatedEvent(
            user_id=self._id.value,
            updated_fields=('profile',)
        ))
    
    def verify_email(self) -> None:
        """验证邮箱"""
        if self._is_email_verified:
            return  # 已验证
        
        self._is_email_verified = True
        self._updated_at = datetime.utcnow()
    
    def deactivate(self, reason: Optional[str] = None) -> None:
        """停用账户"""
        if not self._is_active:
            return  # 已停用
        
        self._is_active = False
        self._updated_at = datetime.utcnow()
        
        self._add_event(UserDeactivatedEvent(
            user_id=self._id.value,
            reason=reason
        ))
    
    def reactivate(self) -> None:
        """重新激活账户"""
        if self._is_active:
            return  # 已激活
        
        self._is_active = True
        self._updated_at = datetime.utcnow()
        
        self._add_event(UserReactivatedEvent(user_id=self._id.value))
    
    def promote_to_role(self, new_role: UserRole) -> None:
        """提升用户角色"""
        if self._role == new_role:
            return
        
        self._role = new_role
        self._updated_at = datetime.utcnow()
    
    # ==================== 查询方法 ====================
    
    def is_admin(self) -> bool:
        """是否为管理员"""
        return self._role == UserRole.ADMIN
    
    def can_perform_admin_action(self) -> bool:
        """是否可以执行管理员操作"""
        return self.is_admin() and self._is_active
    
    # ==================== 事件管理 ====================
    
    def _add_event(self, event: DomainEvent) -> None:
        """添加领域事件到内部队列"""
        self._domain_events.append(event)
    
    def pop_events(self) -> List[DomainEvent]:
        """弹出所有待发布的领域事件
        
        由应用层在保存聚合后调用，获取事件并发布到事件总线。
        """
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id.value)
    
    def __repr__(self) -> str:
        return f"User(id={self._id.value}, username={self._username.value}, email={self._email.value})"
