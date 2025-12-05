


class SocialInteractionService:
    def __init__():
        pass

    def share_post_with_friends(self, post_id: str, sender_id: str, 
                                friend_ids: List[str]):
        """分享帖子给好友 - 跨Post和User聚合"""
        post = self.post_repo.get_by_id(post_id)
        sender = self.user_repo.get_by_id(sender_id)

        # 这里通过事件来提醒帖子已分享，而不是直接操作 好友的聚合
        # TODO：可能要专门写一个领域服务来通知朋友

    