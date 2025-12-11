from shared.event_bus import get_event_bus
from app_social.domain.domain_event.friendship_events import FriendshipAcceptedEvent
from app_social.services.social_service import SocialService

class FriendshipHandler:
    def __init__(self):
        self._social_service = SocialService()

    def handle_friendship_accepted(self, event: FriendshipAcceptedEvent):
        # Create private chat
        print(f"Handling FriendshipAcceptedEvent: {event.friendship_id}. Creating chat between {event.requester_id} and {event.addressee_id}")
        try:
            self._social_service.create_private_chat(event.requester_id, event.addressee_id)
            print("Chat created successfully.")
        except Exception as e:
            print(f"Error creating chat for new friendship: {e}")

def register_friendship_handlers():
    bus = get_event_bus()
    handler = FriendshipHandler()
    bus.subscribe(FriendshipAcceptedEvent, handler.handle_friendship_accepted)
