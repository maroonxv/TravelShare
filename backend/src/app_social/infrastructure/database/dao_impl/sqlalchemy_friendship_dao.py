from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app_social.infrastructure.database.po.friendship_po import FriendshipPO
from app_social.domain.value_objects.friendship_value_objects import FriendshipStatus

class SqlAlchemyFriendshipDao:
    def __init__(self, session: Session):
        self._session = session

    def save(self, po: FriendshipPO) -> None:
        self._session.add(po)

    def find_by_id(self, id: str) -> Optional[FriendshipPO]:
        return self._session.query(FriendshipPO).filter_by(id=id).first()

    def find_by_users(self, user1_id: str, user2_id: str) -> Optional[FriendshipPO]:
        """
        Find friendship where user1 and user2 are participants, regardless of direction.
        """
        return self._session.query(FriendshipPO).filter(
            or_(
                and_(FriendshipPO.requester_id == user1_id, FriendshipPO.addressee_id == user2_id),
                and_(FriendshipPO.requester_id == user2_id, FriendshipPO.addressee_id == user1_id)
            )
        ).first()

    def find_pending_incoming(self, user_id: str) -> List[FriendshipPO]:
        return self._session.query(FriendshipPO).filter(
            FriendshipPO.addressee_id == user_id,
            FriendshipPO.status == FriendshipStatus.PENDING
        ).all()

    def find_pending_outgoing(self, user_id: str) -> List[FriendshipPO]:
        return self._session.query(FriendshipPO).filter(
            FriendshipPO.requester_id == user_id,
            FriendshipPO.status == FriendshipStatus.PENDING
        ).all()

    def find_friends(self, user_id: str) -> List[FriendshipPO]:
        """
        Find all accepted friendships for this user.
        """
        return self._session.query(FriendshipPO).filter(
            or_(
                FriendshipPO.requester_id == user_id,
                FriendshipPO.addressee_id == user_id
            ),
            FriendshipPO.status == FriendshipStatus.ACCEPTED
        ).all()
