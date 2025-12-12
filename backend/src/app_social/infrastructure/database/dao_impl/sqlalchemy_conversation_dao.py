from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, exists, desc, and_, func, insert

from app_social.infrastructure.database.dao_interface.i_conversation_dao import IConversationDao
from app_social.infrastructure.database.persistent_model.conversation_po import ConversationPO, conversation_participants
from app_social.infrastructure.database.persistent_model.message_po import MessagePO

class SqlAlchemyConversationDao(IConversationDao):
    """基于 SQLAlchemy 的会话 DAO 实现"""

    def __init__(self, session: Session):
        self.session = session

    def get_participants_with_roles(self, conversation_id: str) -> List[Dict[str, str]]:
        stmt = select(
            conversation_participants.c.user_id,
            conversation_participants.c.role
        ).where(
            conversation_participants.c.conversation_id == conversation_id
        )
        rows = self.session.execute(stmt).all()
        return [{"user_id": row.user_id, "role": row.role} for row in rows]

    def update_participants(self, conversation_id: str, participants: List[Dict[str, str]]) -> None:
        # 1. Delete existing
        stmt = delete(conversation_participants).where(
            conversation_participants.c.conversation_id == conversation_id
        )
        self.session.execute(stmt)
        
        # 2. Insert new
        if participants:
            values = [
                {
                    "conversation_id": conversation_id, 
                    "user_id": p["user_id"],
                    "role": p["role"]
                } 
                for p in participants
            ]
            stmt = insert(conversation_participants).values(values)
            self.session.execute(stmt)
            
        self.session.flush()

    def find_by_id(self, conversation_id: str) -> Optional[ConversationPO]:
        stmt = select(ConversationPO).where(ConversationPO.id == conversation_id)
        return self.session.execute(stmt).scalars().first()

    def find_by_participants(self, user_id1: str, user_id2: str) -> Optional[ConversationPO]:
        """查找两人之间的私聊 (conversation_type='private')"""
        # 需要找到同时包含 user_id1 和 user_id2 的会话
        # 且类型为 private
        # 这里使用两次 join 或者是子查询
        
        # Alias for participants table to join twice
        p1 = conversation_participants.alias('p1')
        p2 = conversation_participants.alias('p2')
        
        stmt = (
            select(ConversationPO)
            .join(p1, p1.c.conversation_id == ConversationPO.id)
            .join(p2, p2.c.conversation_id == ConversationPO.id)
            .where(
                and_(
                    ConversationPO.conversation_type == 'private',
                    p1.c.user_id == user_id1,
                    p2.c.user_id == user_id2
                )
            )
        )
        return self.session.execute(stmt).scalars().first()

    def find_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[ConversationPO]:
        """获取用户参与的所有会话，按最后消息时间倒序"""
        stmt = (
            select(ConversationPO)
            .join(conversation_participants, conversation_participants.c.conversation_id == ConversationPO.id)
            .where(conversation_participants.c.user_id == user_id)
            .order_by(desc(ConversationPO.last_message_at))
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.execute(stmt).scalars().all())

    def find_by_user_with_unread(self, user_id: str) -> List[ConversationPO]:
        """获取用户有未读消息的会话"""
        # 逻辑：
        # 1. 用户参与的会话
        # 2. 会话中有消息的 read_by_json 不包含 user_id
        # 注意：read_by_json 是字符串，使用 LIKE 进行模糊匹配近似判断
        # JSON 格式为 ["u1", "u2"]，所以匹配 '%"user_id"%'
        
        # 子查询：找到有未读消息的会话ID
        unread_msgs_subquery = (
            select(MessagePO.conversation_id)
            .where(
                and_(
                    MessagePO.read_by_json.not_like(f'%"{user_id}"%'),
                    MessagePO.sender_id != user_id, # 自己发的消息不算未读
                    MessagePO.is_deleted == False
                )
            )
            .distinct()
        )

        stmt = (
            select(ConversationPO)
            .join(conversation_participants, conversation_participants.c.conversation_id == ConversationPO.id)
            .where(
                and_(
                    conversation_participants.c.user_id == user_id,
                    ConversationPO.id.in_(unread_msgs_subquery)
                )
            )
            .order_by(desc(ConversationPO.last_message_at))
        )
        return list(self.session.execute(stmt).scalars().all())

    def add(self, conversation_po: ConversationPO) -> None:
        self.session.add(conversation_po)
        self.session.flush()

    def update(self, conversation_po: ConversationPO) -> None:
        self.session.merge(conversation_po)
        self.session.flush()

    def delete(self, conversation_id: str) -> None:
        # First delete participants association
        stmt_participants = delete(conversation_participants).where(
            conversation_participants.c.conversation_id == conversation_id
        )
        self.session.execute(stmt_participants)
        
        # Messages should be deleted by cascade if configured correctly, 
        # but MessageDAO.delete_by_conversation might be called by repo.
        # Here we just delete the conversation itself.
        stmt = delete(ConversationPO).where(ConversationPO.id == conversation_id)
        self.session.execute(stmt)
        self.session.flush()

    def exists(self, conversation_id: str) -> bool:
        stmt = select(exists().where(ConversationPO.id == conversation_id))
        return self.session.execute(stmt).scalar()
