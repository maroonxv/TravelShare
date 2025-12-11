from sqlalchemy import Column, String, Enum, DateTime, UniqueConstraint, Index
from shared.database.core import Base
from app_social.domain.value_objects.friendship_value_objects import FriendshipStatus
import datetime

class FriendshipPO(Base):
    __tablename__ = "friendships"

    id = Column(String(36), primary_key=True)
    requester_id = Column(String(36), nullable=False)
    addressee_id = Column(String(36), nullable=False)
    status = Column(Enum(FriendshipStatus), nullable=False, default=FriendshipStatus.PENDING)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('requester_id', 'addressee_id', name='uq_friendship_requester_addressee'),
        Index('idx_friendship_requester', 'requester_id'),
        Index('idx_friendship_addressee', 'addressee_id'),
        Index('idx_friendship_status', 'status'),
    )
