from flask import session
from flask_socketio import join_room, leave_room, emit
from shared.infrastructure.socket import socketio
from app_social.domain.domain_event.social_events import MessageSentEvent
from shared.event_bus import get_event_bus
from datetime import datetime
import logging
from shared.database.core import SessionLocal
from app_auth.infrastructure.database.dao_impl.sqlalchemy_user_dao import SqlAlchemyUserDao
from app_auth.infrastructure.database.repository_impl.user_repository_impl import UserRepositoryImpl
from app_auth.domain.value_objects.user_value_objects import UserId

logger = logging.getLogger(__name__)

# ==================== Socket Events ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    user_id = session.get('user_id')
    if user_id:
        logger.info(f"User {user_id} connected to socket")
        join_room(f"user_{user_id}")
    else:
        logger.info("Anonymous user connected")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")

@socketio.on('join')
def on_join(data):
    """Join a conversation room"""
    room = data.get('room')
    if not room:
        return
    
    # TODO: Check permission if user is allowed to join this conversation
    join_room(room)
    logger.info(f"Socket: Joined room {room}")

@socketio.on('leave')
def on_leave(data):
    """Leave a conversation room"""
    room = data.get('room')
    if not room:
        return
    
    leave_room(room)
    logger.info(f"Socket: Left room {room}")

# ==================== Domain Event Handlers ====================

def handle_message_sent(event: MessageSentEvent):
    """
    Push new message to conversation room participants
    """
    logger.info(f"Pushing message {event.message_id} to room {event.conversation_id}")
    
    # Fetch sender info
    sender_name = None
    sender_avatar = None
    
    session_db = SessionLocal()
    try:
        user_dao = SqlAlchemyUserDao(session_db)
        user_repo = UserRepositoryImpl(user_dao)
        user = user_repo.find_by_id(UserId(event.sender_id))
        if user:
            sender_name = user.username.value
            sender_avatar = user.profile.avatar_url
    except Exception as e:
        logger.error(f"Error fetching sender info for socket push: {e}")
    finally:
        session_db.close()

    payload = {
        "id": event.message_id,
        "conversation_id": event.conversation_id,
        "sender_id": event.sender_id,
        "sender_name": sender_name,
        "sender_avatar": sender_avatar,
        "content": event.content,
        "type": event.message_type,
        "media_url": event.media_url, # Ensure media_url is included if present in event
        "reference_id": event.reference_id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    socketio.emit('new_message', payload, room=event.conversation_id)

def register_social_socket_handlers():
    """Register domain event listeners and ensure socket events are loaded"""
    event_bus = get_event_bus()
    # Subscribe using the class name string, which is what event.event_type returns
    event_bus.subscribe(MessageSentEvent.__name__, handle_message_sent)
    logger.info("Social socket handlers registered")
