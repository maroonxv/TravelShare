"""
评论实体 - Post 聚合的子实体
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Comment:
    """评论实体
    
    作为 Post 聚合根的子实体，不能独立存在。
    """
    
    comment_id: str
    post_id: str
    author_id: str
    content: str
    parent_id: Optional[str] = None  # 回复的评论ID，None表示直接评论帖子
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_deleted: bool = False
    
    @classmethod
    def create(
        cls,
        comment_id: str,
        post_id: str,
        author_id: str,
        content: str,
        parent_id: Optional[str] = None
    ) -> 'Comment':
        """创建评论"""
        if not content or not content.strip():
            raise ValueError("Comment content cannot be empty")
        if len(content) > 1000:
            raise ValueError("Comment must be at most 1000 characters")
        
        return cls(
            comment_id=comment_id,
            post_id=post_id,
            author_id=author_id,
            content=content,
            parent_id=parent_id
        )
    
    def is_reply(self) -> bool:
        """是否为回复（而非直接评论）"""
        return self.parent_id is not None
    
    def soft_delete(self) -> None:
        """软删除"""
        self.is_deleted = True
        self.content = "[评论已删除]"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Comment):
            return False
        return self.comment_id == other.comment_id
    
    def __hash__(self) -> int:
        return hash(self.comment_id)