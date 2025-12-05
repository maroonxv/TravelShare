"""
帖子仓库接口
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app_social.domain.aggregate.post_aggregate import Post
from app_social.domain.value_objects.social_value_objects import PostId, PostVisibility


class IPostRepository(ABC):
    """帖子仓库接口"""
    
    @abstractmethod
    def save(self, post: Post) -> None:
        """保存帖子（新增或更新）"""
        pass
    
    @abstractmethod
    def find_by_id(self, post_id: PostId) -> Optional[Post]:
        """根据ID查找帖子"""
        pass
    
    @abstractmethod
    def find_by_author(
        self,
        author_id: str,
        include_deleted: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> List[Post]:
        """查找用户的帖子
        
        Args:
            author_id: 作者ID
            include_deleted: 是否包含已删除的帖子
            limit: 每页数量
            offset: 偏移量
        """
        pass
    
    @abstractmethod
    def find_by_trip(self, trip_id: str) -> Optional[Post]:
        """查找关联旅行的游记"""
        pass
    
    @abstractmethod
    def find_public_feed(
        self,
        limit: int = 20,
        offset: int = 0,
        tags: Optional[List[str]] = None
    ) -> List[Post]:
        """获取公开帖子流
        
        Args:
            limit: 每页数量
            offset: 偏移量
            tags: 标签筛选（可选）
        """
        pass
    
    @abstractmethod
    def find_by_visibility(
        self,
        visibility: PostVisibility,
        limit: int = 20,
        offset: int = 0
    ) -> List[Post]:
        """按可见性查找帖子"""
        pass
    
    @abstractmethod
    def delete(self, post_id: PostId) -> None:
        """删除帖子（物理删除）"""
        pass
    
    @abstractmethod
    def exists(self, post_id: PostId) -> bool:
        """检查帖子是否存在"""
        pass
    
    @abstractmethod
    def count_by_author(self, author_id: str, include_deleted: bool = False) -> int:
        """统计用户的帖子数量"""
        pass
