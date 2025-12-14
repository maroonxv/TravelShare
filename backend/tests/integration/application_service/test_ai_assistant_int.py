
import pytest
import json
from datetime import datetime, date, time
from unittest.mock import MagicMock, patch
from app import create_app
from shared.database.core import SessionLocal, Base, engine
from app_auth.infrastructure.database.persistent_model.user_po import UserPO
from app_travel.infrastructure.database.persistent_model.trip_po import ActivityPO, TripPO, TripDayPO
from app_social.infrastructure.database.persistent_model.post_po import PostPO
from app_ai.infrastructure.database.persistent_model.ai_po import AiConversationPO, AiMessagePO

@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config['TESTING'] = True
    yield app

@pytest.fixture(scope='module')
def client(test_app):
    return test_app.test_client()

@pytest.fixture(scope='function')
def db():
    # Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()
    # Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope='function')
def test_user(db):
    # Clean up first
    # Delete conversations first (cascade to messages)
    db.rollback()
    convs = db.query(AiConversationPO).filter(AiConversationPO.user_id == 'test_user_id').all()
    for c in convs:
        db.delete(c)
    db.commit() # Commit conversation deletion first
    
    db.query(UserPO).filter_by(id='test_user_id').delete()
    db.commit()

    user = UserPO(
        id='test_user_id',
        username='test_user',
        email='test@example.com',
        hashed_password='hashed_password'
    )
    db.add(user)
    db.commit()
    yield user
    # Clean up after
    db.rollback() # Ensure no pending transaction locks
    convs = db.query(AiConversationPO).filter(AiConversationPO.user_id == 'test_user_id').all()
    for c in convs:
        db.delete(c)
    db.commit()
    
    db.delete(user)
    db.commit()

@pytest.fixture(scope='function')
def test_data(db):
    # Clean up first
    db.query(PostPO).filter(PostPO.id.in_(['post_bj', 'post_sh'])).delete(synchronize_session=False)
    db.query(ActivityPO).filter(ActivityPO.id.in_(['act_bj', 'act_sh'])).delete(synchronize_session=False)
    db.query(TripDayPO).filter(TripDayPO.trip_id.in_(['trip_bj', 'trip_sh'])).delete(synchronize_session=False)
    db.query(TripPO).filter(TripPO.id.in_(['trip_bj', 'trip_sh'])).delete(synchronize_session=False)
    db.commit()

    # 1. Beijing Data
    trip_bj = TripPO(
        id='trip_bj',
        name='Beijing Trip',
        creator_id='test_user_id',
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 3),
        visibility='public',
        status='planning'
    )
    db.add(trip_bj)
    
    trip_day_bj = TripDayPO(id=1, trip_id='trip_bj', day_number=1, date=date(2023, 1, 1))
    db.add(trip_day_bj)
    
    # Activity: Great Wall
    activity_bj = ActivityPO(
        id='act_bj',
        trip_day_id=1,
        name='The Great Wall',
        activity_type='sightseeing',
        location_name='Beijing',
        start_time=time(9, 0),
        end_time=time(12, 0),
        notes='Must visit place'
    )
    db.add(activity_bj)
    
    # Post: Beijing
    post_bj = PostPO(
        id='post_bj',
        author_id='test_user_id',
        title='My trip to Beijing',
        text='Beijing is amazing! The food is great.',
        visibility='public'
    )
    db.add(post_bj)

    # 2. Shanghai Data
    trip_sh = TripPO(
        id='trip_sh',
        name='Shanghai Trip',
        creator_id='test_user_id',
        start_date=date(2023, 2, 1),
        end_date=date(2023, 2, 3),
        visibility='public',
        status='planning'
    )
    db.add(trip_sh)

    trip_day_sh = TripDayPO(id=2, trip_id='trip_sh', day_number=1, date=date(2023, 2, 1))
    db.add(trip_day_sh)

    # Activity: The Bund
    activity_sh = ActivityPO(
        id='act_sh',
        trip_day_id=2,
        name='The Bund',
        activity_type='sightseeing',
        location_name='Shanghai',
        start_time=time(19, 0),
        end_time=time(21, 0),
        notes='Beautiful night view'
    )
    db.add(activity_sh)

    # Post: Shanghai
    post_sh = PostPO(
        id='post_sh',
        author_id='test_user_id',
        title='Shanghai Night',
        text='The Bund is spectacular at night.',
        visibility='public'
    )
    db.add(post_sh)
    
    db.commit()
    
    yield
    
    # Cleanup
    db.rollback() # Ensure no pending transaction locks
    db.query(PostPO).filter(PostPO.id.in_(['post_bj', 'post_sh'])).delete(synchronize_session=False)
    db.query(ActivityPO).filter(ActivityPO.id.in_(['act_bj', 'act_sh'])).delete(synchronize_session=False)
    db.query(TripDayPO).filter(TripDayPO.trip_id.in_(['trip_bj', 'trip_sh'])).delete(synchronize_session=False)
    db.query(TripPO).filter(TripPO.id.in_(['trip_bj', 'trip_sh'])).delete(synchronize_session=False)
    db.commit()

@patch('app_ai.infrastructure.llm.langchain_deepseek_adapter.LangChainDeepSeekAdapter.stream_chat')
def test_rag_retrieval_beijing(mock_stream_chat, client, db, test_user, test_data):
    """
    Test that querying for 'Beijing' retrieves Beijing-related activities and posts,
    and passes them to the LLM.
    """
    # Setup Mock
    mock_stream_chat.return_value = ["Here is info about ", "Beijing."]
    
    payload = {
        "user_id": test_user.id,
        "message": "Tell me about Beijing"
    }
    
    response = client.post('/api/ai/chat', json=payload)
    assert response.status_code == 200
    
    # Consume stream
    _ = response.data 
    
    # Verify LLM call arguments
    assert mock_stream_chat.called
    call_args = mock_stream_chat.call_args
    # call_args[0] is args, [1] is kwargs. 
    # stream_chat(messages, system_prompt)
    system_prompt = call_args[0][1] 
    
    # Verify System Prompt contains retrieved info
    assert "The Great Wall" in system_prompt
    assert "My trip to Beijing" in system_prompt
    
    # Verify System Prompt DOES NOT contain Shanghai info (relevance check)
    assert "The Bund" not in system_prompt
    assert "Shanghai Night" not in system_prompt

    # Verify Database Persistence of Attachments
    db.commit() # End current transaction to see changes from App
    # We need to find the conversation created
    conv = db.query(AiConversationPO).filter(AiConversationPO.user_id == test_user.id).first()
    assert conv is not None
    last_msg = conv.messages[-1]
    assert last_msg.role == 'assistant'
    
    # Check attachments in DB
    assert last_msg.attachments_json is not None
    attachments = json.loads(last_msg.attachments_json)
    
    # Should have at least one attachment related to Beijing
    titles = [a['title'] for a in attachments]
    assert "The Great Wall" in titles or "My trip to Beijing" in titles

@patch('app_ai.infrastructure.llm.langchain_deepseek_adapter.LangChainDeepSeekAdapter.stream_chat')
def test_rag_retrieval_shanghai(mock_stream_chat, client, db, test_user, test_data):
    """
    Test that querying for 'Shanghai' retrieves Shanghai-related info.
    """
    mock_stream_chat.return_value = ["Shanghai info."]
    
    payload = {
        "user_id": test_user.id,
        "message": "What to do in Shanghai?"
    }
    
    response = client.post('/api/ai/chat', json=payload)
    assert response.status_code == 200
    # Consume stream to trigger execution
    _ = response.data
    response.close() # Ensure stream is closed and DB session released
    
    # Check LLM Prompt
    assert mock_stream_chat.called
    
    # Verify retrieval context
    call_args = mock_stream_chat.call_args
    # call_args[0] is args, call_args[1] is kwargs
    # stream_chat(history, system_prompt)
    
    system_prompt = call_args[0][1]
    
    assert "The Bund" in system_prompt
    assert "Shanghai" in system_prompt

@patch('app_ai.infrastructure.llm.langchain_deepseek_adapter.LangChainDeepSeekAdapter.stream_chat')
def test_rag_no_relevant_info(mock_stream_chat, client, db, test_user, test_data):
    """
    Test querying for something not in DB.
    """
    mock_stream_chat.return_value = ["I don't know."]
    
    payload = {
        "user_id": test_user.id,
        "message": "Paris"
    }
    
    response = client.post('/api/ai/chat', json=payload)
    assert response.status_code == 200
    
    # Consume stream to trigger execution
    _ = response.data
    response.close()

    assert mock_stream_chat.called
    
    # Verify retrieval context
    call_args = mock_stream_chat.call_args
    # stream_chat(history, system_prompt)
    system_prompt = call_args[0][1]
    
    # Should not contain specific trip info
    assert "The Great Wall" not in system_prompt

@patch('app_ai.infrastructure.llm.langchain_deepseek_adapter.LangChainDeepSeekAdapter.stream_chat')
def test_conversation_history_passed_to_llm(mock_stream_chat, client, db, test_user):
    """
    Test that previous messages in the conversation are passed to the LLM.
    """
    # Cleanup first
    db.query(AiMessagePO).filter(AiMessagePO.conversation_id == 'hist_conv').delete()
    db.query(AiConversationPO).filter(AiConversationPO.id == 'hist_conv').delete()
    db.commit()

    # Create existing conversation
    conv = AiConversationPO(id='hist_conv', user_id=test_user.id, title='History Chat')
    msg1 = AiMessagePO(conversation_id='hist_conv', role='user', content='My name is Alice', created_at=datetime(2023,1,1,10,0))
    msg2 = AiMessagePO(conversation_id='hist_conv', role='assistant', content='Hello Alice', created_at=datetime(2023,1,1,10,1))
    db.add(conv)
    db.add(msg1)
    db.add(msg2)
    db.commit()
    
    mock_stream_chat.return_value = ["Hello again."]
    
    payload = {
        "user_id": test_user.id,
        "conversation_id": "hist_conv",
        "message": "What is my name?"
    }
    
    response = client.post('/api/ai/chat', json=payload)
    assert response.status_code == 200
    
    # Check LLM args
    assert mock_stream_chat.called
    call_args = mock_stream_chat.call_args
    messages_arg = call_args[0][0] if call_args[0] else call_args[1].get('messages')
    
    # Should contain: History(User) -> History(AI) -> New(User)
    # But note: The domain service might or might not include the *current* user message in the 'history' passed to stream_chat, 
    # OR it passes it as the last message.
    # Let's check AiChatDomainService.stream_chat:
    #   history = conversation.get_history_for_llm()
    #   ... llm_client.stream_chat(history, system_prompt)
    # And conversation.add_message is called BEFORE stream_response.
    # So history should include the new message.
    
    assert len(messages_arg) == 3
    assert messages_arg[0].content == 'My name is Alice'
    assert messages_arg[0].role == 'user'
    assert messages_arg[1].content == 'Hello Alice'
    assert messages_arg[1].role == 'assistant'
    assert messages_arg[2].content == 'What is my name?'
    assert messages_arg[2].role == 'user'

def test_delete_conversation(client, db, test_user):
    """
    Test deleting a conversation.
    """
    # Cleanup
    db.query(AiMessagePO).filter(AiMessagePO.conversation_id == 'del_conv').delete()
    db.query(AiConversationPO).filter(AiConversationPO.id == 'del_conv').delete()
    db.commit()

    # 1. Create conversation
    conv = AiConversationPO(id='del_conv', user_id=test_user.id, title='To Delete')
    db.add(conv)
    db.commit()
    
    # 2. Verify it exists via API
    resp = client.get(f'/api/ai/conversations?user_id={test_user.id}')
    assert resp.status_code == 200
    data = resp.json
    assert any(c['id'] == 'del_conv' for c in data)
    
    # 2. Delete conversation
    # Soft delete
    # Pass user_id to authorize the deletion
    response = client.delete(f'/api/ai/conversations/del_conv?user_id={test_user.id}')
    assert response.status_code == 200
    
    # 3. Verify
    db.commit() # End transaction to see changes
    # Should still exist but be soft deleted? 
    # The requirement said "delete conversation". If it's hard delete:
    # conv = db.query(AiConversationPO).filter_by(id='del_conv').first()
    # assert conv is None
    
    # If soft delete:
    conv = db.query(AiConversationPO).filter_by(id='del_conv').first()
    assert conv is not None
    assert conv.is_deleted == True

def test_delete_conversation_unauthorized(client, db, test_user):
    """
    Test deleting someone else's conversation.
    """
    # Cleanup
    db.query(AiConversationPO).filter(AiConversationPO.id == 'alice_conv').delete()
    db.query(UserPO).filter(UserPO.id == 'alice').delete()
    db.commit()

    # Create Alice
    alice = UserPO(id='alice', username='alice', email='alice@test.com', hashed_password='pw')
    db.add(alice)
    db.commit()

    # Alice's conversation
    conv = AiConversationPO(id='alice_conv', user_id='alice', title='Alice Chat')
    db.add(conv)
    db.commit()
    
    
    # Try to delete Alice's conversation as test_user
    # Current impl of delete endpoint gets user_id from query param or session?
    # Assuming session or query param. If we use test_user context:
    
    # We need to simulate being test_user but targeting alice_conv
    # But delete endpoint usually takes conversation_id. 
    # And verifies ownership.
    
    # If we are logged in as test_user (via session/client)
    # Note: ai_view.py might not use session directly if auth middleware is not fully mocked.
    # So we pass user_id explicitly to simulate the authenticated request.
    
    response = client.delete(f'/api/ai/conversations/alice_conv?user_id={test_user.id}')
    
    # Should fail (403 or 404)
    assert response.status_code in [403, 404]
