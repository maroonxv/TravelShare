from dataclasses import dataclass

@dataclass
class UserDescription:
    """用户简介值对象 - 用于展示，避免引用User聚合根"""
    user_id: str
    nickname: str
    avatar_url: str # 头像url
    

    