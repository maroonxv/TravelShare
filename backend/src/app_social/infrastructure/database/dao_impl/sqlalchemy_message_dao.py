from typing import List, Optional, Set
import json
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, update, and_, asc

from app_social.infrastructure.database.dao_interface.i_message_dao import IMessageDao
from app_social.infrastructure.database.persistent_model.message_po import MessagePO

class SqlAlchemyMessageDao(IMessageDao):
    """基于 SQLAlchemy 的消息 DAO 实现"""

    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, message_id: str) -> Optional[MessagePO]:
        stmt = select(MessagePO).where(MessagePO.id == message_id)
        return self.session.execute(stmt).scalars().first()

    def find_by_conversation(
        self, 
        conversation_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[MessagePO]:
        stmt = (
            select(MessagePO)
            .where(
                and_(
                    MessagePO.conversation_id == conversation_id,
                    MessagePO.is_deleted == False
                )
            )
            .order_by(asc(MessagePO.sent_at)) # 消息通常按时间正序显示
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.execute(stmt).scalars().all())

    def add(self, message_po: MessagePO) -> None:
        self.session.add(message_po)
        self.session.flush()

    def update(self, message_po: MessagePO) -> None:
        self.session.merge(message_po)
        self.session.flush()

    def delete(self, message_id: str) -> None:
        # 逻辑删除
        stmt = (
            update(MessagePO)
            .where(MessagePO.id == message_id)
            .values(is_deleted=True)
        )
        self.session.execute(stmt)
        self.session.flush()

    def delete_by_conversation(self, conversation_id: str) -> None:
        # 物理删除或逻辑删除？通常随会话删除是物理删除
        stmt = delete(MessagePO).where(MessagePO.conversation_id == conversation_id)
        self.session.execute(stmt)
        self.session.flush()

    def mark_read(self, message_id: str, user_id: str) -> None:
        """标记消息为已读"""
        # 需要先读取，修改 JSON，再保存
        # 这是一个“读取-修改-写入”的操作，在并发下可能不安全
        # 但对于已读状态，覆盖是可以接受的，或者使用乐观锁
        # 这里简单实现：
        message = self.find_by_id(message_id)
        if message:
            read_by = set(json.loads(message.read_by_json))
            if user_id not in read_by:
                read_by.add(user_id)
                message.read_by_json = json.dumps(list(read_by))
                self.session.add(message) # Re-add to session to ensure update
                self.session.flush()

    def mark_all_read(self, conversation_id: str, user_id: str) -> int:
        """标记会话中所有消息为已读"""
        # 找出所有未读消息
        stmt = select(MessagePO).where(
            and_(
                MessagePO.conversation_id == conversation_id,
                MessagePO.read_by_json.not_like(f'%"{user_id}"%'),
                MessagePO.sender_id != user_id,
                MessagePO.is_deleted == False
            )
        )
        messages = list(self.session.execute(stmt).scalars().all())
        
        count = 0
        for msg in messages:
            read_by = set(json.loads(msg.read_by_json))
            if user_id not in read_by:
                read_by.add(user_id)
                msg.read_by_json = json.dumps(list(read_by))
                self.session.add(msg)
                count += 1
        
        self.session.flush()
        return count
