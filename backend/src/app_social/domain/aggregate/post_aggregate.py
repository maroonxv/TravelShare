"""
Post 聚合根 - 充血模型

管理帖子及其评论、点赞。
可关联到旅行(trip_id)作为游记。
"""
from datetime import datetime
from typing import List, Optional
import uuid

from app_social.domain.value_objects.social_value_objects import (
    PostId, PostContent, PostVisibility
)
from app_social.domain.entity.comment_entity import Comment
from app_social.domain.entity.like_entity import Like
from app_social.domain.domain_event.social_events import (
    DomainEvent, PostCreatedEvent, PostUpdatedEvent, PostDeletedEvent,
    PostVisibilityChangedEvent, CommentAddedEvent, CommentRemovedEvent,
    PostLikedEvent, PostUnlikedEvent, PostSharedEvent
)


class Post:
    """帖子聚合根 - 充血模型
    
    包含帖子及其评论、点赞的所有业务逻辑。
    """
    
    def __init__(
        self,
        post_id: PostId,
        author_id: str,
        content: PostContent,
        visibility: PostVisibility = PostVisibility.PUBLIC,
        trip_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_deleted: bool = False
    ):
        self._id = post_id
        self._author_id = author_id
        self._content = content
        self._visibility = visibility
        self._trip_id = trip_id  # 关联的旅行ID（游记）
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or self._created_at
        self._is_deleted = is_deleted
        self._comments: List[Comment] = []
        self._likes: List[Like] = []
        self._domain_events: List[DomainEvent] = []
    
    # ==================== 工厂方法 ====================
    
    @classmethod
    def create(
        cls,
        author_id: str,
        content: PostContent,
        visibility: PostVisibility = PostVisibility.PUBLIC,
        trip_id: Optional[str] = None
    ) -> 'Post':
        """创建新帖子"""
        post = cls(
            post_id=PostId.generate(),
            author_id=author_id,
            content=content,
            visibility=visibility,
            trip_id=trip_id
        )
        
        post._add_event(PostCreatedEvent(
            post_id=post.id.value,
            author_id=author_id,
            title=content.title,
            visibility=visibility.value,
            trip_id=trip_id
        ))
        
        return post
    
    @classmethod
    def create_travel_log(
        cls,
        author_id: str,
        trip_id: str,
        content: PostContent
    ) -> 'Post':
        """创建游记 - 关联旅行的帖子"""
        return cls.create(
            author_id=author_id,
            content=content,
            visibility=PostVisibility.PUBLIC,
            trip_id=trip_id
        )
    
    @classmethod
    def reconstitute(
        cls,
        post_id: PostId,
        author_id: str,
        content: PostContent,
        comments: List[Comment],
        likes: List[Like],
        visibility: PostVisibility = PostVisibility.PUBLIC,
        trip_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_deleted: bool = False
    ) -> 'Post':
        """从持久化数据重建帖子"""
        post = cls(
            post_id=post_id,
            author_id=author_id,
            content=content,
            visibility=visibility,
            trip_id=trip_id,
            created_at=created_at,
            updated_at=updated_at,
            is_deleted=is_deleted
        )
        post._comments = comments
        post._likes = likes
        return post
    
    # ==================== 属性访问器 ====================
    
    @property
    def id(self) -> PostId:
        return self._id
    
    @property
    def author_id(self) -> str:
        return self._author_id
    
    @property
    def content(self) -> PostContent:
        return self._content
    
    @property
    def visibility(self) -> PostVisibility:
        return self._visibility
    
    @property
    def trip_id(self) -> Optional[str]:
        return self._trip_id
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def is_deleted(self) -> bool:
        return self._is_deleted
    
    @property
    def comments(self) -> List[Comment]:
        return [c for c in self._comments if not c.is_deleted]
    
    @property
    def likes(self) -> List[Like]:
        return self._likes.copy()
    
    @property
    def like_count(self) -> int:
        return len(self._likes)
    
    @property
    def comment_count(self) -> int:
        return len([c for c in self._comments if not c.is_deleted])
    
    @property
    def is_travel_log(self) -> bool:
        """是否为游记"""
        return self._trip_id is not None
    
    # ==================== 内容管理 ====================
    
    def update_content(self, new_content: PostContent) -> None:
        """更新内容"""
        if self._is_deleted:
            raise ValueError("Cannot update deleted post")
        
        self._content = new_content
        self._updated_at = datetime.utcnow()
        
        self._add_event(PostUpdatedEvent(
            post_id=self._id.value,
            author_id=self._author_id,
            updated_fields=('content',)
        ))
    
    def change_visibility(self, new_visibility: PostVisibility) -> None:
        """更改可见性"""
        if self._is_deleted:
            raise ValueError("Cannot change visibility of deleted post")
        
        if self._visibility == new_visibility:
            return
        
        old_visibility = self._visibility
        self._visibility = new_visibility
        self._updated_at = datetime.utcnow()
        
        self._add_event(PostVisibilityChangedEvent(
            post_id=self._id.value,
            old_visibility=old_visibility.value,
            new_visibility=new_visibility.value
        ))
    
    def soft_delete(self) -> None:
        """软删除帖子"""
        if self._is_deleted:
            return
        
        self._is_deleted = True
        self._updated_at = datetime.utcnow()
        
        self._add_event(PostDeletedEvent(
            post_id=self._id.value,
            author_id=self._author_id
        ))
    
    # ==================== 评论管理 ====================
    
    def add_comment(
        self,
        commenter_id: str,
        content: str,
        parent_comment_id: Optional[str] = None
    ) -> Comment:
        """添加评论
        
        Args:
            commenter_id: 评论者ID
            content: 评论内容
            parent_comment_id: 回复的评论ID（可选）
            
        Returns:
            创建的评论实体
        """
        if self._is_deleted:
            raise ValueError("Cannot comment on deleted post")
        
        # 如果是回复，检查父评论是否存在
        if parent_comment_id:
            parent = self._find_comment(parent_comment_id)
            if not parent or parent.is_deleted:
                raise ValueError("Parent comment not found or deleted")
        
        comment = Comment.create(
            comment_id=str(uuid.uuid4()),
            post_id=self._id.value,
            author_id=commenter_id,
            content=content,
            parent_id=parent_comment_id
        )
        
        self._comments.append(comment)
        self._updated_at = datetime.utcnow()
        
        self._add_event(CommentAddedEvent(
            post_id=self._id.value,
            comment_id=comment.comment_id,
            author_id=commenter_id,
            post_author_id=self._author_id,
            parent_comment_id=parent_comment_id
        ))
        
        return comment
    
    def remove_comment(self, comment_id: str, operator_id: str) -> None:
        """删除评论
        
        仅评论作者或帖子作者可删除。
        
        Args:
            comment_id: 评论ID
            operator_id: 操作者ID
        """
        comment = self._find_comment(comment_id)
        if not comment:
            raise ValueError("Comment not found")
        
        # 权限检查
        if operator_id not in [comment.author_id, self._author_id]:
            raise ValueError("Not authorized to delete this comment")
        
        comment.soft_delete()
        self._updated_at = datetime.utcnow()
        
        self._add_event(CommentRemovedEvent(
            post_id=self._id.value,
            comment_id=comment_id,
            removed_by=operator_id
        ))
    
    def _find_comment(self, comment_id: str) -> Optional[Comment]:
        """查找评论"""
        for comment in self._comments:
            if comment.comment_id == comment_id:
                return comment
        return None
    
    # ==================== 点赞管理 ====================
    
    def like(self, user_id: str) -> bool:
        """点赞
        
        Args:
            user_id: 点赞用户ID
            
        Returns:
            如果是新点赞返回 True，已点赞返回 False
        """
        if self._is_deleted:
            raise ValueError("Cannot like deleted post")
        
        # 检查是否已点赞（幂等操作）
        if self._find_like(user_id):
            return False
        
        like = Like(
            user_id=user_id,
            post_id=self._id.value
        )
        self._likes.append(like)
        
        # 仅当非自己点赞时发布事件
        if user_id != self._author_id:
            self._add_event(PostLikedEvent(
                post_id=self._id.value,
                user_id=user_id,
                post_author_id=self._author_id
            ))
        
        return True
    
    def unlike(self, user_id: str) -> bool:
        """取消点赞
        
        Returns:
            如果成功取消返回 True，未点赞返回 False
        """
        like = self._find_like(user_id)
        if not like:
            return False
        
        self._likes.remove(like)
        
        self._add_event(PostUnlikedEvent(
            post_id=self._id.value,
            user_id=user_id
        ))
        
        return True
    
    def is_liked_by(self, user_id: str) -> bool:
        """检查是否被某用户点赞"""
        return self._find_like(user_id) is not None
    
    def _find_like(self, user_id: str) -> Optional[Like]:
        """查找点赞"""
        for like in self._likes:
            if like.user_id == user_id:
                return like
        return None
    
    # ==================== 分享 ====================
    
    def share_to(self, sharer_id: str, recipient_ids: List[str]) -> None:
        """分享帖子给其他用户"""
        if self._is_deleted:
            raise ValueError("Cannot share deleted post")
        
        if not recipient_ids:
            raise ValueError("Must specify at least one recipient")
        
        self._add_event(PostSharedEvent(
            post_id=self._id.value,
            sharer_id=sharer_id,
            shared_to_ids=tuple(recipient_ids)
        ))
    
    # ==================== 权限检查 ====================
    
    def can_be_viewed_by(self, user_id: str) -> bool:
        """检查用户是否可以查看此帖子"""
        if self._is_deleted:
            return False
        
        if self._visibility == PostVisibility.PUBLIC:
            return True
        
        if user_id == self._author_id:
            return True
        
        if self._visibility == PostVisibility.PRIVATE:
            return False
        
        # FRIENDS visibility 需要检查好友关系，由应用层处理
        return True
    
    def can_be_edited_by(self, user_id: str) -> bool:
        """检查用户是否可以编辑此帖子"""
        return user_id == self._author_id and not self._is_deleted
    
    # ==================== 事件管理 ====================
    
    def _add_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)
    
    def pop_events(self) -> List[DomainEvent]:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Post):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id.value)
    
    def __repr__(self) -> str:
        return f"Post(id={self._id.value}, title={self._content.title[:20]}...)"