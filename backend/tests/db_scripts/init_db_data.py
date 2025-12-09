import sys
import os
import uuid
import json
from datetime import datetime

# Add backend/src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from shared.database.core import SessionLocal
from app_auth.infrastructure.database.persistent_model.user_po import UserPO
from app_auth.infrastructure.database.dao_impl.sqlalchemy_user_dao import SqlAlchemyUserDao

from app_travel.infrastructure.database.persistent_model.trip_po import TripPO, TripDayPO
from app_travel.infrastructure.database.dao_impl.sqlalchemy_trip_dao import SqlAlchemyTripDao

from app_social.infrastructure.database.persistent_model.post_po import PostPO
from app_social.infrastructure.database.dao_impl.sqlalchemy_post_dao import SqlAlchemyPostDao

from app_social.infrastructure.database.persistent_model.conversation_po import ConversationPO
from app_social.infrastructure.database.dao_impl.sqlalchemy_conversation_dao import SqlAlchemyConversationDao

from app_social.infrastructure.database.persistent_model.message_po import MessagePO
from app_social.infrastructure.database.dao_impl.sqlalchemy_message_dao import SqlAlchemyMessageDao

# Hardcoded IDs for predictability
USER1_ID = "11111111-1111-1111-1111-111111111111"
USER2_ID = "22222222-2222-2222-2222-222222222222"
TRIP_ID = "33333333-3333-3333-3333-333333333333"
POST_ID = "44444444-4444-4444-4444-444444444444"
CONV_ID = "55555555-5555-5555-5555-555555555555"
MSG_ID = "66666666-6666-6666-6666-666666666666"

def init_data():
    session = SessionLocal()
    try:
        print("Initializing data...")
        
        # 1. Users
        user_dao = SqlAlchemyUserDao(session)
        
        # User 1
        if not user_dao.find_by_id(USER1_ID):
            user1 = UserPO(
                id=USER1_ID,
                username="test_user_1",
                email="user1@example.com",
                hashed_password="hashed_secret",
                role="user",
                bio="I love traveling!",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            user_dao.add(user1)
            print(f"Added User: {user1.username}")
        else:
            print(f"User {USER1_ID} already exists.")

        # User 2
        if not user_dao.find_by_id(USER2_ID):
            user2 = UserPO(
                id=USER2_ID,
                username="test_user_2",
                email="user2@example.com",
                hashed_password="hashed_secret",
                role="user",
                bio="Photography enthusiast.",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            user_dao.add(user2)
            print(f"Added User: {user2.username}")
        else:
            print(f"User {USER2_ID} already exists.")
        
        # 2. Trip
        trip_dao = SqlAlchemyTripDao(session)
        if not trip_dao.find_by_id(TRIP_ID):
            trip = TripPO(
                id=TRIP_ID,
                name="Summer Vacation in Paris",
                description="A wonderful week in Paris.",
                creator_id=USER1_ID,
                start_date=datetime.now().date(),
                end_date=datetime.now().date(),
                visibility="public",
                status="planning",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            # Add a day
            day1 = TripDayPO(
                trip_id=TRIP_ID,
                day_number=1,
                date=datetime.now().date(),
                theme="Arrival"
            )
            trip.days.append(day1)
            
            trip_dao.add(trip)
            print(f"Added Trip: {trip.name}")
        else:
            print(f"Trip {TRIP_ID} already exists.")

        # 3. Post
        post_dao = SqlAlchemyPostDao(session)
        if not post_dao.find_by_id(POST_ID):
            post = PostPO(
                id=POST_ID,
                author_id=USER1_ID,
                title="My Paris Plan",
                text="Here is my plan for Paris!",
                visibility="public",
                trip_id=TRIP_ID,
                is_deleted=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                images_json='[]',
                tags_json='["travel", "paris"]'
            )
            post_dao.add(post)
            print(f"Added Post: {post.title}")
        else:
            print(f"Post {POST_ID} already exists.")

        # 4. Conversation & Message
        conv_dao = SqlAlchemyConversationDao(session)
        if not conv_dao.find_by_id(CONV_ID):
            conv = ConversationPO(
                id=CONV_ID,
                conversation_type="private",
                title=None,
                created_at=datetime.utcnow(),
                last_message_at=datetime.utcnow()
            )
            conv_dao.add(conv)
            # Add participants
            conv_dao.update_participants(CONV_ID, [USER1_ID, USER2_ID])
            print(f"Added Conversation: {CONV_ID}")
            
            # Message
            msg_dao = SqlAlchemyMessageDao(session)
            msg = MessagePO(
                id=MSG_ID,
                conversation_id=CONV_ID,
                sender_id=USER1_ID,
                content_text="Hi, nice trip plan!",
                message_type="text",
                sent_at=datetime.utcnow(),
                is_deleted=False,
                read_by_json='[]'
            )
            msg_dao.add(msg)
            print(f"Added Message: {msg.content_text}")
        else:
            print(f"Conversation {CONV_ID} already exists.")

        session.commit()
        print("Data initialization completed successfully.")

    except Exception as e:
        session.rollback()
        print(f"Error initializing data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    init_data()
