import pytest
import time
from flask_socketio import SocketIOTestClient
from app import create_app
from shared.infrastructure.socket import socketio
from app_social.services.social_service import SocialService
from shared.database.core import SessionLocal
from app_auth.infrastructure.database.dao_impl.sqlalchemy_user_dao import SqlAlchemyUserDao
from app_auth.infrastructure.database.repository_impl.user_repository_impl import UserRepositoryImpl
from app_auth.domain.value_objects.user_value_objects import UserId
from app_social.domain.value_objects.social_value_objects import ConversationId
from app_social.infrastructure.database.dao_impl.sqlalchemy_conversation_dao import SqlAlchemyConversationDao
from app_social.infrastructure.database.dao_impl.sqlalchemy_message_dao import SqlAlchemyMessageDao
from app_social.infrastructure.database.repository_impl.conversation_repository_impl import ConversationRepositoryImpl
from app_social.domain.aggregate.conversation_aggregate import Conversation
from shared.event_bus import get_event_bus
from app_social.domain.domain_event.social_events import MessageSentEvent

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def socket_client(app, client):
    """
    Create a SocketIO test client.
    Note: Flask-SocketIO test client needs the app and the flask test client.
    """
    return socketio.test_client(app, flask_test_client=client)

@pytest.fixture
def social_service():
    return SocialService()

def test_realtime_message_push(app, client, social_service):
    """
    Test that when a message is sent via SocialService (mimicking the REST API),
    a WebSocket event 'new_message' is emitted to the correct room.
    """
    # 1. Setup: Create two users and a conversation
    # We need to manually setup data because we are in an integration test
    # Or we can mock the IDs if we trust the Service logic. 
    # Let's use real DB interactions to be safe, or just mock IDs if we only test the Event -> Socket path.
    # To be "high coverage" for the communication part, we need to ensure the EventBus is working.
    
    # Let's create a conversation first using Service or Domain
    user1_id = "user_test_1"
    user2_id = "user_test_2"
    
    # Create a conversation directly in DB or via Service?
    # Service.create_private_chat is complex (needs friends). 
    # Let's direct create Conversation Aggregate and save it to simplify setup, 
    # as we focus on "MessageSentEvent -> Socket Emit"
    
    # Actually, the user complained that "sending message (via API)" doesn't trigger update.
    # So we should call `social_service.send_message`.
    
    # We need to bypass "friendship check" if we use create_private_chat, 
    # or just manually insert a conversation into DB.
    
    session = SessionLocal()
    try:
        # Create conversation manually
        conv = Conversation.create_private(user1_id, user2_id)
        conv_id = conv.id.value
        
        conv_dao = SqlAlchemyConversationDao(session)
        msg_dao = SqlAlchemyMessageDao(session)
        conv_repo = ConversationRepositoryImpl(conv_dao, msg_dao)
        conv_repo.save(conv)
        session.commit()
    finally:
        session.close()

    # 2. Connect Socket Client for User 2 (The Receiver)
    # Simulate User 2 logging in and connecting
    with client.session_transaction() as sess:
        sess['user_id'] = user2_id
    
    # Initialize SocketIO Test Client
    # Namespace is usually '/'
    socket_client = socketio.test_client(app, flask_test_client=client)
    
    # Ensure connected
    assert socket_client.is_connected()
    
    # User 2 joins the conversation room
    # The frontend logic is: socket.emit('join', { room: activeConvId })
    socket_client.emit('join', {'room': conv_id})
    
    # Give it a moment to process join
    time.sleep(0.1)
    
    # 3. Action: User 1 sends a message via SocialService (The REST API path)
    # This should trigger MessageSentEvent -> EventBus -> Socket Handler -> Emit
    msg_content = "Hello Realtime World"
    
    # We need to ensure the request context or app context is active if Service uses it?
    # SocialService uses SessionLocal, so it should be fine.
    # But EventBus is a singleton.
    
    social_service.send_message(
        conversation_id=conv_id,
        sender_id=user1_id,
        content=msg_content,
        message_type="text"
    )
    
    # 4. Assert: User 2 received 'new_message' event
    received = socket_client.get_received()
    
    # Filter for 'new_message' events
    message_events = [evt for evt in received if evt['name'] == 'new_message']
    
    assert len(message_events) > 0, "No 'new_message' event received by the client"
    
    event_data = message_events[0]['args'][0]
    assert event_data['content'] == msg_content
    assert event_data['conversation_id'] == conv_id
    assert event_data['sender_id'] == user1_id
    
    # 5. Test Leave Room
    socket_client.emit('leave', {'room': conv_id})
    
    # Send another message
    social_service.send_message(
        conversation_id=conv_id,
        sender_id=user1_id,
        content="Should not be received",
        message_type="text"
    )
    
    # Check received again
    received_after = socket_client.get_received()
    message_events_after = [evt for evt in received_after if evt['name'] == 'new_message']
    
    assert len(message_events_after) == 0, "Client received message after leaving the room"

