from dataclasses import dataclass
from datetime import datetime
from shared.domain_event import DomainEvent

@dataclass(frozen=True)
class FriendRequestSentEvent(DomainEvent):
    friendship_id: str
    requester_id: str
    addressee_id: str
    sent_at: datetime

@dataclass(frozen=True)
class FriendshipAcceptedEvent(DomainEvent):
    friendship_id: str
    requester_id: str
    addressee_id: str
    accepted_at: datetime

@dataclass(frozen=True)
class FriendshipRejectedEvent(DomainEvent):
    friendship_id: str
    requester_id: str
    addressee_id: str
    rejected_at: datetime
