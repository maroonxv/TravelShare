import pytest
import uuid
import os
import sys
import shutil
from unittest.mock import patch
from werkzeug.datastructures import FileStorage
from io import BytesIO

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from app_social.services.social_service import SocialService
from app_social.domain.value_objects.social_value_objects import ConversationType

@pytest.fixture
def social_service(db_session):
    # Mocking SessionLocal to return the test db_session
    # This ensures that the service uses the same session as the test
    with patch('app_social.services.social_service.SessionLocal', return_value=db_session):
        service = SocialService()
        # Mock storage
        test_upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_uploads_chat")
        if os.path.exists(test_upload_folder):
            shutil.rmtree(test_upload_folder)
        os.makedirs(test_upload_folder)
        
        # We need to access the storage service instance inside social_service
        service._storage_service.upload_folder = test_upload_folder
        
        yield service
        
        if os.path.exists(test_upload_folder):
            shutil.rmtree(test_upload_folder)

class TestCommunicationImageUrl:
    
    def test_send_image_message(self, social_service, db_session):
        """Test sending an image message"""
        user1 = str(uuid.uuid4())
        user2 = str(uuid.uuid4())
        
        # 1. Create Private Chat
        # Note: In real app, they might need to be friends. 
        # But create_private_chat implementation in service currently comments out strict friendship check 
        # or it might have been enabled. Let's assume it allows it or we mock friendship if needed.
        # Looking at code read earlier, friendship check is commented out or optional?
        # "Enforce Friendship Requirement... We need to check friendship status... if not friendship... raise ValueError"
        # It seems it WAS commented out in the Read output.
        
        conv_res = social_service.create_private_chat(user1, user2)
        conv_id = conv_res["conversation_id"]
        
        # 2. Create Dummy Image
        dummy_file = FileStorage(
            stream=BytesIO(b"fake image content"),
            filename="chat_image.jpg",
            content_type="image/jpeg"
        )
        
        # 3. Send Image Message
        msg_res = social_service.send_message(
            conversation_id=conv_id,
            sender_id=user1,
            content="Look at this",
            message_type="image",
            media_file=dummy_file
        )
        
        assert msg_res["message_id"] is not None
        assert msg_res["media_url"] is not None
        assert "chat_images" in msg_res["media_url"]
        
        # 4. Verify in DB/Service Retrieval
        # We need to commit/expire to ensure we read back from DB
        db_session.expire_all()
        
        # We need to make sure the service method `get_conversation_messages` uses the same session or we mock it too.
        # The fixture `social_service` patches SessionLocal, so any call inside `social_service` uses `db_session`.
        
        messages = social_service.get_conversation_messages(conv_id, user1)
        
        last_msg = messages[-1]
        assert last_msg["type"] == "image"
        assert last_msg["content"] == "Look at this"
        assert last_msg["media_url"] == msg_res["media_url"]
        
    def test_share_post_message(self, social_service, db_session):
        """Test sharing a post in chat"""
        user1 = str(uuid.uuid4())
        user2 = str(uuid.uuid4())
        
        # 1. Create Private Chat
        conv_res = social_service.create_private_chat(user1, user2)
        conv_id = conv_res["conversation_id"]
        
        # 2. Create a Post to share
        post_res = social_service.create_post(
            author_id=user1,
            title="My Post",
            content="Content"
        )
        post_id = post_res["post_id"]
        
        # 3. Share Post
        msg_res = social_service.send_message(
            conversation_id=conv_id,
            sender_id=user1,
            content="Check my post",
            message_type="share_post",
            reference_id=post_id
        )
        
        assert msg_res["reference_id"] == post_id
        
        # 4. Verify retrieval
        db_session.expire_all()
        messages = social_service.get_conversation_messages(conv_id, user2)
        last_msg = messages[-1]
        assert last_msg["type"] == "share_post"
        assert last_msg["reference_id"] == post_id
        assert last_msg["content"] == "Check my post"

    def test_share_non_existent_post(self, social_service, db_session):
        """Test error when sharing non-existent post"""
        user1 = str(uuid.uuid4())
        user2 = str(uuid.uuid4())
        conv_res = social_service.create_private_chat(user1, user2)
        conv_id = conv_res["conversation_id"]
        
        with pytest.raises(ValueError, match="Post not found"):
            social_service.send_message(
                conversation_id=conv_id,
                sender_id=user1,
                content="Check",
                message_type="share_post",
                reference_id="non-existent-id-123"
            )
