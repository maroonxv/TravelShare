from dataclasses import dataclass
from enum import Enum
from typing import Tuple

@dataclass(frozen=True)
class FriendshipId:
    """Friendship Unique Identifier"""
    value: str

    def __str__(self):
        return self.value

class FriendshipStatus(Enum):
    """Friendship Status Enum"""
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"

@dataclass(frozen=True)
class Relation:
    """
    Represents the relationship pair (requester_id, addressee_id).
    Ensures that (A, B) is treated uniquely in business semantics where order matters for request,
    but checking existence might need consideration of both directions depending on requirements.
    For this specific object, it preserves the direction of the request or relationship.
    """
    requester_id: str
    addressee_id: str

    def __post_init__(self):
        if self.requester_id == self.addressee_id:
            raise ValueError("Requester and addressee cannot be the same person.")
