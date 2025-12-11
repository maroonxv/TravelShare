from typing import List, Optional
from app_social.domain.demand_interface.friendship_repository import IFriendshipRepository
from app_social.domain.aggregate.friendship_aggregate import Friendship
from app_social.domain.value_objects.friendship_value_objects import (
    FriendshipId, FriendshipStatus, Relation
)
from app_social.infrastructure.database.dao_impl.sqlalchemy_friendship_dao import SqlAlchemyFriendshipDao
from app_social.infrastructure.database.po.friendship_po import FriendshipPO

class FriendshipRepositoryImpl(IFriendshipRepository):
    def __init__(self, dao: SqlAlchemyFriendshipDao):
        self._dao = dao

    def save(self, friendship: Friendship) -> None:
        po = self._to_po(friendship)
        # SQLAlchemy merge or add. Since we might have existing entity.
        # Ideally DAO 'save' handles add. For updates, if object is attached to session it tracks changes.
        # But if we constructed a new PO from Entity, we usually need to merge or specific logic.
        # Let's check DAO impl. It uses `session.add`.
        # If PO is already in identity map, `add` is fine.
        # If we created a new PO instance here, we might need to query first or use merge.
        # Simple approach: Query PO by ID, update fields. Or use merge if DAO supports it.
        # Let's rely on DAO save (add) for new, and for existing we might need to copy fields if detached.
        # BUT, standard DDD Repo: save(aggregate).
        # We usually convert aggregate -> PO.
        # If we just do session.add(po), and po has an ID that exists, SA might error or update depending on state.
        # Let's try to lookup existing PO first to be safe, or assume session management handles it (e.g. merge).
        # For this implementation, let's look up existing PO to update, or create new.
        
        existing_po = self._dao.find_by_id(friendship.id.value)
        if existing_po:
            existing_po.status = friendship.status
            existing_po.updated_at = friendship.updated_at
            # Relation usually immutable but for completeness:
            existing_po.requester_id = friendship.requester_id
            existing_po.addressee_id = friendship.addressee_id
        else:
            po = self._to_po(friendship)
            self._dao.save(po)

    def find_by_id(self, friendship_id: FriendshipId) -> Optional[Friendship]:
        po = self._dao.find_by_id(friendship_id.value)
        if po:
            return self._to_domain(po)
        return None

    def find_by_users(self, user1_id: str, user2_id: str) -> Optional[Friendship]:
        po = self._dao.find_by_users(user1_id, user2_id)
        if po:
            return self._to_domain(po)
        return None

    def find_pending_requests(self, user_id: str, type: str = 'incoming') -> List[Friendship]:
        if type == 'incoming':
            pos = self._dao.find_pending_incoming(user_id)
        else:
            pos = self._dao.find_pending_outgoing(user_id)
        return [self._to_domain(po) for po in pos]

    def find_friends(self, user_id: str) -> List[str]:
        pos = self._dao.find_friends(user_id)
        friend_ids = []
        for po in pos:
            if po.requester_id == user_id:
                friend_ids.append(po.addressee_id)
            else:
                friend_ids.append(po.requester_id)
        return friend_ids

    def _to_po(self, friendship: Friendship) -> FriendshipPO:
        return FriendshipPO(
            id=friendship.id.value,
            requester_id=friendship.requester_id,
            addressee_id=friendship.addressee_id,
            status=friendship.status,
            created_at=friendship.created_at,
            updated_at=friendship.updated_at
        )

    def _to_domain(self, po: FriendshipPO) -> Friendship:
        return Friendship(
            id=FriendshipId(po.id),
            relation=Relation(po.requester_id, po.addressee_id),
            status=po.status,
            created_at=po.created_at,
            updated_at=po.updated_at
        )
