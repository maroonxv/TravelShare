"""
Conversation aggregate.
"""

from datetime import datetime
import uuid
from typing import Dict, Iterable, List, Optional, Set, Union

from app_social.domain.domain_event.social_events import (
    ConversationCreatedEvent,
    DomainEvent,
    MessageDeletedEvent,
    MessagesReadEvent,
    MessageSentEvent,
    ParticipantAddedEvent,
    ParticipantRemovedEvent,
)
from app_social.domain.entity.message_entity import Message
from app_social.domain.value_objects.social_value_objects import (
    ConversationId,
    ConversationRole,
    ConversationType,
    MessageContent,
)


class Conversation:
    def __init__(
        self,
        conversation_id: ConversationId,
        participants: Dict[str, ConversationRole],
        conversation_type: ConversationType = ConversationType.PRIVATE,
        created_at: Optional[datetime] = None,
        last_message_at: Optional[datetime] = None,
        title: Optional[str] = None,
    ):
        self._id = conversation_id
        self._participants = participants
        self._conversation_type = conversation_type
        self._created_at = created_at or datetime.utcnow()
        self._last_message_at = last_message_at
        self._title = title
        self._messages: List[Message] = []
        self._domain_events: List[DomainEvent] = []

    @classmethod
    def create_private(cls, initiator_id: str, participant_id: str) -> "Conversation":
        if initiator_id == participant_id:
            raise ValueError("Cannot create conversation with yourself")

        participants = {
            initiator_id: ConversationRole.MEMBER,
            participant_id: ConversationRole.MEMBER,
        }

        conversation = cls(
            conversation_id=ConversationId.generate(),
            participants=participants,
            conversation_type=ConversationType.PRIVATE,
        )
        conversation._add_event(
            ConversationCreatedEvent(
                conversation_id=conversation.id.value,
                creator_id=initiator_id,
                participant_ids=tuple(conversation.participant_ids),
                conversation_type="private",
            )
        )
        return conversation

    @classmethod
    def create_group(
        cls,
        creator_id: str,
        participant_ids: List[str],
        title: Optional[str] = None,
    ) -> "Conversation":
        unique_participants = set(participant_ids)
        unique_participants.discard(creator_id)

        all_ids = {creator_id} | unique_participants
        if len(all_ids) < 2:
            raise ValueError("Group chat requires at least 2 participants")

        participants = {creator_id: ConversationRole.OWNER}
        for participant_id in unique_participants:
            participants[participant_id] = ConversationRole.MEMBER

        conversation = cls(
            conversation_id=ConversationId.generate(),
            participants=participants,
            conversation_type=ConversationType.GROUP,
            title=title,
        )
        conversation._add_event(
            ConversationCreatedEvent(
                conversation_id=conversation.id.value,
                creator_id=creator_id,
                participant_ids=tuple(conversation.participant_ids),
                conversation_type="group",
            )
        )
        return conversation

    @classmethod
    def reconstitute(
        cls,
        conversation_id: ConversationId,
        participants: Optional[Union[Dict[str, ConversationRole], Iterable[str]]] = None,
        messages: Optional[List[Message]] = None,
        conversation_type: ConversationType = ConversationType.PRIVATE,
        created_at: Optional[datetime] = None,
        last_message_at: Optional[datetime] = None,
        title: Optional[str] = None,
        participant_ids: Optional[Iterable[str]] = None,
    ) -> "Conversation":
        normalized_participants = cls._normalize_participants(
            participants if participants is not None else participant_ids
        )
        conversation = cls(
            conversation_id=conversation_id,
            participants=normalized_participants,
            conversation_type=conversation_type,
            created_at=created_at,
            last_message_at=last_message_at,
            title=title,
        )
        conversation._messages = messages or []
        return conversation

    @staticmethod
    def _normalize_participants(
        participants: Optional[Union[Dict[str, ConversationRole], Iterable[str]]]
    ) -> Dict[str, ConversationRole]:
        if participants is None:
            return {}

        if isinstance(participants, dict):
            normalized: Dict[str, ConversationRole] = {}
            for user_id, role in participants.items():
                if isinstance(role, ConversationRole):
                    normalized[user_id] = role
                else:
                    try:
                        normalized[user_id] = ConversationRole(role)
                    except ValueError:
                        normalized[user_id] = ConversationRole.MEMBER
            return normalized

        return {user_id: ConversationRole.MEMBER for user_id in participants}

    @property
    def id(self) -> ConversationId:
        return self._id

    @property
    def participant_ids(self) -> Set[str]:
        return set(self._participants.keys())

    @property
    def participants_with_roles(self) -> Dict[str, ConversationRole]:
        return self._participants.copy()

    def get_role(self, user_id: str) -> Optional[ConversationRole]:
        return self._participants.get(user_id)

    @property
    def conversation_type(self) -> ConversationType:
        return self._conversation_type

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def last_message_at(self) -> Optional[datetime]:
        return self._last_message_at

    @property
    def title(self) -> Optional[str]:
        return self._title

    @property
    def messages(self) -> List[Message]:
        return [message for message in self._messages if not message.is_deleted]

    @property
    def message_count(self) -> int:
        return len(self.messages)

    @property
    def participant_count(self) -> int:
        return len(self._participants)

    @property
    def is_group(self) -> bool:
        return self._conversation_type == ConversationType.GROUP

    def send_message(self, sender_id: str, content: MessageContent) -> Message:
        if sender_id not in self._participants:
            raise ValueError("Sender is not a participant of this conversation")

        message = Message.create(
            message_id=str(uuid.uuid4()),
            conversation_id=self._id.value,
            sender_id=sender_id,
            content=content,
        )
        self._messages.append(message)
        self._last_message_at = message.sent_at

        recipient_ids = [participant_id for participant_id in self._participants if participant_id != sender_id]
        self._add_event(
            MessageSentEvent(
                conversation_id=self._id.value,
                message_id=message.message_id,
                sender_id=sender_id,
                recipient_ids=tuple(recipient_ids),
                message_type=content.message_type,
                content=content.text,
                media_url=content.media_url,
                reference_id=content.reference_id,
            )
        )
        return message

    def delete_message(self, message_id: str, deleted_by: str) -> None:
        message = self._find_message(message_id)
        if not message:
            raise ValueError("Message not found")
        if message.sender_id != deleted_by:
            raise ValueError("Only sender can delete the message")

        message.soft_delete()
        self._add_event(
            MessageDeletedEvent(
                conversation_id=self._id.value,
                message_id=message_id,
                deleted_by=deleted_by,
            )
        )

    def mark_as_read(self, user_id: str, up_to_message_id: Optional[str] = None) -> int:
        if user_id not in self._participants:
            raise ValueError("User is not a participant")

        count = 0
        for message in self._messages:
            if message.is_deleted:
                continue
            if message.mark_read_by(user_id):
                count += 1
            if up_to_message_id and message.message_id == up_to_message_id:
                break

        if count > 0:
            self._add_event(
                MessagesReadEvent(
                    conversation_id=self._id.value,
                    user_id=user_id,
                    up_to_message_id=up_to_message_id or (self._messages[-1].message_id if self._messages else ""),
                )
            )

        return count

    def get_unread_count(self, user_id: str) -> int:
        if user_id not in self._participants:
            return 0

        count = 0
        for message in self._messages:
            if not message.is_deleted and not message.is_read_by(user_id):
                count += 1
        return count

    def get_recent_messages(self, limit: int = 50) -> List[Message]:
        return self.messages[-limit:]

    def _find_message(self, message_id: str) -> Optional[Message]:
        for message in self._messages:
            if message.message_id == message_id:
                return message
        return None

    def add_participant(self, user_id: str, added_by: str) -> None:
        if not self.is_group:
            raise ValueError("Cannot add participants to private conversation")
        if added_by not in self._participants:
            raise ValueError("Only participants can add new members")
        if user_id in self._participants:
            return

        self._participants[user_id] = ConversationRole.MEMBER
        self._add_event(
            ParticipantAddedEvent(
                conversation_id=self._id.value,
                user_id=user_id,
                added_by=added_by,
            )
        )

    def remove_participant(self, user_id: str, removed_by: str) -> None:
        if not self.is_group:
            raise ValueError("Cannot remove participants from private conversation")

        target_role = self._participants.get(user_id)
        if not target_role:
            raise ValueError("User is not a participant")

        operator_role = self._participants.get(removed_by)
        if not operator_role:
            raise ValueError("Operator is not a participant")

        if user_id != removed_by:
            raise ValueError("Can only remove yourself")
        if target_role == ConversationRole.OWNER and len(self._participants) > 1:
            raise ValueError("Owner cannot leave group without transferring ownership")
        if len(self._participants) <= 2:
            raise ValueError("Cannot have less than 2 participants")

        del self._participants[user_id]
        self._add_event(
            ParticipantRemovedEvent(
                conversation_id=self._id.value,
                user_id=user_id,
                removed_by=removed_by,
            )
        )

    def change_role(self, target_user_id: str, new_role: ConversationRole, operator_id: str) -> None:
        if not self.is_group:
            raise ValueError("Only group chats have roles")

        target_role = self._participants.get(target_user_id)
        if not target_role:
            raise ValueError("Target user is not a participant")

        operator_role = self._participants.get(operator_id)
        if not operator_role:
            raise ValueError("Operator is not a participant")
        if operator_role != ConversationRole.OWNER:
            raise ValueError("Only owner can change roles")
        if target_user_id == operator_id and new_role != ConversationRole.OWNER:
            raise ValueError("Owner cannot demote self directly. Use transfer_ownership.")
        if new_role == ConversationRole.OWNER:
            raise ValueError("Use transfer_ownership to change owner")

        self._participants[target_user_id] = new_role

    def transfer_ownership(self, new_owner_id: str, operator_id: str) -> None:
        if not self.is_group:
            raise ValueError("Only group chats have owners")
        if operator_id not in self._participants or self._participants[operator_id] != ConversationRole.OWNER:
            raise ValueError("Only owner can transfer ownership")
        if new_owner_id not in self._participants:
            raise ValueError("New owner must be a participant")

        self._participants[operator_id] = ConversationRole.ADMIN
        self._participants[new_owner_id] = ConversationRole.OWNER

    def update_title(self, new_title: str, updated_by: str) -> None:
        if not self.is_group:
            raise ValueError("Cannot set title for private conversation")
        if updated_by not in self._participants:
            raise ValueError("Only participants can update title")
        self._title = new_title

    def is_participant(self, user_id: str) -> bool:
        return user_id in self._participants

    def get_other_participant(self, user_id: str) -> Optional[str]:
        if self.is_group or user_id not in self._participants:
            return None

        for participant_id in self._participants:
            if participant_id != user_id:
                return participant_id
        return None

    def _add_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pop_events(self) -> List[DomainEvent]:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Conversation):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id.value)

    def __repr__(self) -> str:
        return f"Conversation(id={self._id.value}, type={self._conversation_type.value}, participants={len(self._participants)})"
