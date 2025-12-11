from datetime import datetime
from typing import List, Optional
import uuid

from app_social.domain.value_objects.friendship_value_objects import (
    FriendshipId, FriendshipStatus, Relation
)
from app_social.domain.domain_event.friendship_events import (
    FriendRequestSentEvent, FriendshipAcceptedEvent, FriendshipRejectedEvent
)
from shared.domain_event import DomainEvent

class Friendship:
    """
    Friendship Aggregate Root.
    Manages the lifecycle of a friendship between two users.
    """
    def __init__(
        self,
        id: FriendshipId,
        relation: Relation,
        status: FriendshipStatus,
        created_at: datetime,
        updated_at: datetime
    ):
        self._id = id
        self._relation = relation
        self._status = status
        self._created_at = created_at
        self._updated_at = updated_at
        self._domain_events: List[DomainEvent] = []

    @property
    def id(self) -> FriendshipId:
        return self._id

    @property
    def requester_id(self) -> str:
        return self._relation.requester_id

    @property
    def addressee_id(self) -> str:
        return self._relation.addressee_id

    @property
    def status(self) -> FriendshipStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @staticmethod
    def create(requester_id: str, addressee_id: str) -> 'Friendship':
        """Factory method to create a new friendship request."""
        now = datetime.now()
        friendship_id = FriendshipId(str(uuid.uuid4()))
        relation = Relation(requester_id, addressee_id)
        
        friendship = Friendship(
            id=friendship_id,
            relation=relation,
            status=FriendshipStatus.PENDING,
            created_at=now,
            updated_at=now
        )
        
        friendship._add_event(FriendRequestSentEvent(
            friendship_id=friendship_id.value,
            requester_id=requester_id,
            addressee_id=addressee_id,
            sent_at=now
        ))
        
        return friendship

    def accept(self, operator_id: str) -> None:
        """Accept a friend request."""
        if self._status != FriendshipStatus.PENDING:
            raise ValueError("Can only accept pending friend requests.")
        
        if operator_id != self.addressee_id:
            raise ValueError("Only the addressee can accept the friend request.")
            
        self._status = FriendshipStatus.ACCEPTED
        self._updated_at = datetime.now()
        
        self._add_event(FriendshipAcceptedEvent(
            friendship_id=self.id.value,
            requester_id=self.requester_id,
            addressee_id=self.addressee_id,
            accepted_at=self._updated_at
        ))

    def reject(self, operator_id: str) -> None:
        """Reject a friend request."""
        if self._status != FriendshipStatus.PENDING:
            raise ValueError("Can only reject pending friend requests.")

        if operator_id != self.addressee_id:
             # Depending on requirements, maybe requester can also 'cancel' it?
             # For now, let's assume only addressee rejects, or we can allow requester to cancel.
             # If strict interpretation of "Reject", it's usually the addressee.
             # If we want "Cancel", it's the requester.
             # Let's interpret "reject" as addressee action for now.
             # If requester wants to cancel, maybe we need a cancel() method or allow reject to be called by requester (acting as cancel)
             # Let's stick to requirements: "Reject() : Only PENDING state can execute."
             pass
        
        # Checking operator permissions
        if operator_id != self.addressee_id and operator_id != self.requester_id:
             raise ValueError("Permission denied.")

        self._status = FriendshipStatus.REJECTED
        self._updated_at = datetime.now()
        
        self._add_event(FriendshipRejectedEvent(
            friendship_id=self.id.value,
            requester_id=self.requester_id,
            addressee_id=self.addressee_id,
            rejected_at=self._updated_at
        ))

    def block(self, operator_id: str) -> None:
        """Block the other user."""
        # Block can happen at any state? Usually yes.
        # Who is blocking whom? 
        # If A blocks B, the friendship status becomes BLOCKED.
        # But who initiates?
        # If aggregate root represents "Relationship between A and B", a single status BLOCKED might be ambiguous (who blocked who?).
        # Usually Blocking is a separate entity/table or a directed status.
        # BUT, defined in requirements: "status: Pending/accepted/blocked". 
        # "Block(): Any state can transition to BLOCKED".
        # This implies standard simplistic model where if one blocks, the relationship is blocked.
        
        if operator_id != self.requester_id and operator_id != self.addressee_id:
            raise ValueError("Permission denied.")
            
        self._status = FriendshipStatus.BLOCKED
        self._updated_at = datetime.now()
        # No specific event requested for Blocked, but good practice to add one? 
        # Requirement only asked for RequestSent, Accepted, Rejected. I will skip BlockedEvent for now to stick to spec.

    def _add_event(self, event: DomainEvent):
        self._domain_events.append(event)
        
    def pop_events(self) -> List[DomainEvent]:
        events = self._domain_events[:]
        self._domain_events.clear()
        return events
