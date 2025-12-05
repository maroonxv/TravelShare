"""
旅行成员实体
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app_travel.domain.value_objects.travel_value_objects import MemberRole


@dataclass
class TripMember:
    """旅行成员实体
    
    表示参与旅行的成员，包含成员角色和加入时间。
    作为 Trip 聚合根的子实体。
    """
    
    user_id: str
    role: MemberRole
    joined_at: datetime = field(default_factory=datetime.utcnow)
    nickname: Optional[str] = None  # 在该旅行中的昵称
    
    @classmethod
    def create_admin(cls, user_id: str, nickname: Optional[str] = None) -> 'TripMember':
        """创建管理员成员（通常是创建者）"""
        return cls(
            user_id=user_id,
            role=MemberRole.ADMIN,
            nickname=nickname
        )
    
    @classmethod
    def create_member(cls, user_id: str, nickname: Optional[str] = None) -> 'TripMember':
        """创建普通成员"""
        return cls(
            user_id=user_id,
            role=MemberRole.MEMBER,
            nickname=nickname
        )
    
    def is_admin(self) -> bool:
        """是否为管理员"""
        return self.role == MemberRole.ADMIN
    
    def promote_to_admin(self) -> None:
        """提升为管理员"""
        self.role = MemberRole.ADMIN
    
    def demote_to_member(self) -> None:
        """降级为普通成员"""
        self.role = MemberRole.MEMBER
    
    def update_nickname(self, nickname: Optional[str]) -> None:
        """更新昵称"""
        self.nickname = nickname
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TripMember):
            return False
        return self.user_id == other.user_id
    
    def __hash__(self) -> int:
        return hash(self.user_id)