"""
点赞实体
"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Like:
    """点赞实体
    
    作为 Post 聚合根的子实体。
    """
    
    user_id: str
    post_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Like):
            return False
        return self.user_id == other.user_id and self.post_id == other.post_id
    
    def __hash__(self) -> int:
        return hash((self.user_id, self.post_id))