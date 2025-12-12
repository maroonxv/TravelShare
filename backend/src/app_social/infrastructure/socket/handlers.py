from flask import session
from flask_socketio import join_room, leave_room, emit
from shared.infrastructure.socket import socketio
from app_social.domain.domain_event.social_events import MessageSentEvent
from shared.event_bus import get_event_bus
from datetime import datetime
import logging

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
    
    payload = {
        "id": event.message_id,
        "conversation_id": event.conversation_id,
        "sender_id": event.sender_id,
        "content": event.content,
        "type": event.message_type,
        "created_at": datetime.utcnow().isoformat()
    }
    
    socketio.emit('new_message', payload, room=event.conversation_id)

def register_social_socket_handlers():
    """Register domain event listeners and ensure socket events are loaded"""
    event_bus = get_event_bus()
    # Subscribe using the class name string, which is what event.event_type returns
    event_bus.subscribe(MessageSentEvent.__name__, handle_message_sent)
    logger.info("Social socket handlers registered")
