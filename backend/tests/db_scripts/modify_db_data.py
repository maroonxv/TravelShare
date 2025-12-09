import sys
import os
import uuid
import json
from datetime import datetime

# Add backend/src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from shared.database.core import SessionLocal
from app_auth.infrastructure.database.dao_impl.sqlalchemy_user_dao import SqlAlchemyUserDao
from app_travel.infrastructure.database.dao_impl.sqlalchemy_trip_dao import SqlAlchemyTripDao
from app_social.infrastructure.database.dao_impl.sqlalchemy_post_dao import SqlAlchemyPostDao
from app_social.infrastructure.database.dao_impl.sqlalchemy_conversation_dao import SqlAlchemyConversationDao
from app_social.infrastructure.database.dao_impl.sqlalchemy_message_dao import SqlAlchemyMessageDao

# Hardcoded IDs for predictability
USER1_ID = "11111111-1111-1111-1111-111111111111"
USER2_ID = "22222222-2222-2222-2222-222222222222"
TRIP_ID = "33333333-3333-3333-3333-333333333333"
POST_ID = "44444444-4444-4444-4444-444444444444"
CONV_ID = "55555555-5555-5555-5555-555555555555"
MSG_ID = "66666666-6666-6666-6666-666666666666"

def modify_data():
    session = SessionLocal()
    try:
        print("Modifying data...")
        
        # 1. Update User
        user_dao = SqlAlchemyUserDao(session)
        user1 = user_dao.find_by_id(USER1_ID)
        if user1:
            user1.bio = "I REALLY love traveling! (Updated)"
            user1.updated_at = datetime.utcnow()
            user_dao.update(user1)
            print(f"Updated User: {user1.username} bio")
        else:
            print(f"User {USER1_ID} not found.")

        # 2. Update Trip
        trip_dao = SqlAlchemyTripDao(session)
        trip = trip_dao.find_by_id(TRIP_ID)
        if trip:
            trip.status = "ongoing"
            trip.updated_at = datetime.utcnow()
            trip_dao.update(trip)
            print(f"Updated Trip: {trip.name} status to ongoing")
        else:
            print(f"Trip {TRIP_ID} not found.")

        # 3. Update Post
        post_dao = SqlAlchemyPostDao(session)
        post = post_dao.find_by_id(POST_ID)
        if post:
            post.title = "My Paris Plan (Updated)"
            post.updated_at = datetime.utcnow()
            # Assuming tags_json is a simple string for now, but should ideally parse/dump
            # But let's just update the title
            post_dao.update(post)
            print(f"Updated Post: {post.title}")
        else:
            print(f"Post {POST_ID} not found.")

        session.commit()
        print("Data modification completed successfully.")

    except Exception as e:
        session.rollback()
        print(f"Error modifying data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    modify_data()
