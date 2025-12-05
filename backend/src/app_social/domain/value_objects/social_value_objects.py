"""
app_social 值对象定义
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple
import uuid


@dataclass(frozen=True)
class PostId:
    """帖子唯一标识"""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("PostId cannot be empty")
    
    @classmethod
    def generate(cls) -> 'PostId':
        return cls(str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ConversationId:
    """会话唯一标识"""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("ConversationId cannot be empty")
    
    @classmethod
    def generate(cls) -> 'ConversationId':
        return cls(str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PostContent:
    """帖子内容值对象 - 不可变"""
    title: str
    text: str
    images: Tuple[str, ...] = ()  # 图片URL列表
    tags: Tuple[str, ...] = ()    # 标签列表
    
    TITLE_MAX_LENGTH = 200
    TEXT_MAX_LENGTH = 10000
    MAX_IMAGES = 9
    MAX_TAGS = 10
    
    def __post_init__(self):
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if len(self.title) > self.TITLE_MAX_LENGTH:
            raise ValueError(f"Title must be at most {self.TITLE_MAX_LENGTH} characters")
        if not self.text or not self.text.strip():
            raise ValueError("Text cannot be empty")
        if len(self.text) > self.TEXT_MAX_LENGTH:
            raise ValueError(f"Text must be at most {self.TEXT_MAX_LENGTH} characters")
        if len(self.images) > self.MAX_IMAGES:
            raise ValueError(f"Cannot have more than {self.MAX_IMAGES} images")
        if len(self.tags) > self.MAX_TAGS:
            raise ValueError(f"Cannot have more than {self.MAX_TAGS} tags")
    
    @property
    def summary(self) -> str:
        """获取内容摘要（前100字）"""
        return self.text[:100] + "..." if len(self.text) > 100 else self.text


@dataclass(frozen=True)
class MessageContent:
    """消息内容值对象"""
    text: str
    message_type: str = "text"  # text, image, location, trip_share
    attachment_url: Optional[str] = None
    
    TEXT_MAX_LENGTH = 2000
    
    def __post_init__(self):
        if self.message_type == "text" and (not self.text or not self.text.strip()):
            raise ValueError("Text message cannot be empty")
        if self.text and len(self.text) > self.TEXT_MAX_LENGTH:
            raise ValueError(f"Message must be at most {self.TEXT_MAX_LENGTH} characters")
        if self.message_type in ["image", "location", "trip_share"] and not self.attachment_url:
            raise ValueError(f"{self.message_type} message requires attachment_url")
    
    @classmethod
    def text_message(cls, text: str) -> 'MessageContent':
        """创建文本消息"""
        return cls(text=text, message_type="text")
    
    @classmethod
    def image_message(cls, image_url: str, caption: str = "") -> 'MessageContent':
        """创建图片消息"""
        return cls(text=caption, message_type="image", attachment_url=image_url)
    
    @classmethod
    def location_message(cls, location_url: str, description: str = "") -> 'MessageContent':
        """创建位置消息"""
        return cls(text=description, message_type="location", attachment_url=location_url)
    
    @classmethod
    def trip_share_message(cls, trip_id: str, message: str = "") -> 'MessageContent':
        """创建旅行分享消息"""
        return cls(text=message, message_type="trip_share", attachment_url=trip_id)


class PostVisibility(Enum):
    """帖子可见性枚举"""
    PUBLIC = "public"     # 公开
    FRIENDS = "friends"   # 好友可见
    PRIVATE = "private"   # 仅自己可见
    
    @classmethod
    def from_string(cls, visibility_str: str) -> 'PostVisibility':
        visibility_str = visibility_str.lower()
        for visibility in cls:
            if visibility.value == visibility_str:
                return visibility
        raise ValueError(f"Unknown visibility: {visibility_str}")


class ConversationType(Enum):
    """会话类型枚举"""
    PRIVATE = "private"  # 私聊（一对一）
    GROUP = "group"      # 群聊


@dataclass(frozen=True)
class CommentContent:
    """评论内容值对象"""
    text: str
    
    MAX_LENGTH = 1000
    
    def __post_init__(self):
        if not self.text or not self.text.strip():
            raise ValueError("Comment cannot be empty")
        if len(self.text) > self.MAX_LENGTH:
            raise ValueError(f"Comment must be at most {self.MAX_LENGTH} characters")
