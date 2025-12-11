from abc import ABC, abstractmethod
from typing import List, Optional
from app_social.domain.aggregate.friendship_aggregate import Friendship
from app_social.domain.value_objects.friendship_value_objects import FriendshipId, Relation

class IFriendshipRepository(ABC):
    @abstractmethod
    def save(self, friendship: Friendship) -> None:
        pass

    @abstractmethod
    def find_by_id(self, friendship_id: FriendshipId) -> Optional[Friendship]:
        pass

    @abstractmethod
    def find_by_users(self, user1_id: str, user2_id: str) -> Optional[Friendship]:
        """Find friendship between two users regardless of who is requester."""
        pass

    @abstractmethod
    def find_pending_requests(self, user_id: str, type: str = 'incoming') -> List[Friendship]:
        """
        Find pending requests.
        type: 'incoming' (user is addressee) or 'outgoing' (user is requester)
        """
        pass

    @abstractmethod
    def find_friends(self, user_id: str) -> List[str]:
        """Return list of friend user_ids."""
        pass
