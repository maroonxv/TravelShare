

class Conversation:
    """聊天聚合根"""
    def __init__(self, conversation_id: str, participant_ids: List[str]):
        self.id = id
        self.participant_ids = participant_ids  # 参与者ID列表
        self.created_at = datetime.now()
        self.last_message_at = None