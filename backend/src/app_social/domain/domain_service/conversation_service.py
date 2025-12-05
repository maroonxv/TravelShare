

class ConversationService:
    

    def create_conversation(self, initiator_id: str, participant_ids: List[str]):
        """创建会话 - 需要验证好友关系"""
        # TODO：验证好友关系，这里怎么验证？

        # 创建会话
        conversation = Conversation(
            id=generate_id(),
            participant_ids=all_participants
        )
        return conversation