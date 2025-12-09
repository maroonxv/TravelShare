import sys
import os
import uuid
from datetime import datetime

# Add backend/src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from shared.database.core import SessionLocal
from app_auth.infrastructure.database.dao_impl.sqlalchemy_user_dao import SqlAlchemyUserDao
from app_travel.infrastructure.database.dao_impl.sqlalchemy_trip_dao import SqlAlchemyTripDao
from app_social.infrastructure.database.dao_impl.sqlalchemy_post_dao import SqlAlchemyPostDao
from app_social.infrastructure.database.dao_impl.sqlalchemy_conversation_dao import SqlAlchemyConversationDao
from app_social.infrastructure.database.persistent_model.conversation_po import ConversationPO
from app_social.infrastructure.database.persistent_model.message_po import MessagePO
from app_travel.infrastructure.database.persistent_model.trip_po import TripDayPO, TripMemberPO, ActivityPO, TransitPO
from sqlalchemy import delete, select

# Hardcoded IDs for predictability
USER1_ID = "11111111-1111-1111-1111-111111111111"
USER2_ID = "22222222-2222-2222-2222-222222222222"
TRIP_ID = "33333333-3333-3333-3333-333333333333"
POST_ID = "44444444-4444-4444-4444-444444444444"
CONV_ID = "55555555-5555-5555-5555-555555555555"
MSG_ID = "66666666-6666-6666-6666-666666666666"

def delete_data():
    session = SessionLocal()
    try:
        print("Deleting data...")
        
        # 1. Delete Message & Conversation
        # Conversation deletion often requires cleaning up messages and participants first
        # But if we use ORM cascade correctly, deleting ConversationPO should suffice.
        # However, SqlAlchemyConversationDao.delete() does a simple delete(ConversationPO)
        # which might trigger DB constraints if ON DELETE CASCADE is not set in DB.
        # Safe bet: Delete Message first.
        
        # Manually delete messages for the conversation
        stmt = delete(MessagePO).where(MessagePO.conversation_id == CONV_ID)
        session.execute(stmt)
        print(f"Deleted Messages for Conversation: {CONV_ID}")
        
        conv_dao = SqlAlchemyConversationDao(session)
        if conv_dao.find_by_id(CONV_ID):
            # The DAO's delete method deletes the conversation
            # Participants are in a separate table. If mapped via relationship/secondary, SQLAlchemy handles it.
            # If manual table, we might need to clean up.
            # SqlAlchemyConversationDao.update_participants does delete/insert.
            # Let's try to clear participants first.
            conv_dao.update_participants(CONV_ID, [])
            
            conv_dao.delete(CONV_ID)
            print(f"Deleted Conversation: {CONV_ID}")
        else:
            print(f"Conversation {CONV_ID} not found.")

        # 2. Delete Post
        post_dao = SqlAlchemyPostDao(session)
        if post_dao.find_by_id(POST_ID):
            post_dao.delete(POST_ID)
            print(f"Deleted Post: {POST_ID}")
        else:
            print(f"Post {POST_ID} not found.")

        # 3. Delete Trip
        trip_dao = SqlAlchemyTripDao(session)
        if trip_dao.find_by_id(TRIP_ID):
            # Manually delete Trip dependencies to avoid foreign key constraints
            # 1. TripMembers
            stmt = delete(TripMemberPO).where(TripMemberPO.trip_id == TRIP_ID)
            session.execute(stmt)
            
            # 2. TripDays and their Activities/Transits
            # Get all trip day IDs
            stmt = select(TripDayPO.id).where(TripDayPO.trip_id == TRIP_ID)
            trip_day_ids = session.execute(stmt).scalars().all()
            
            if trip_day_ids:
                # Delete Activities
                stmt = delete(ActivityPO).where(ActivityPO.trip_day_id.in_(trip_day_ids))
                session.execute(stmt)
                
                # Delete Transits
                stmt = delete(TransitPO).where(TransitPO.trip_day_id.in_(trip_day_ids))
                session.execute(stmt)
                
                # Delete TripDays
                stmt = delete(TripDayPO).where(TripDayPO.trip_id == TRIP_ID)
                session.execute(stmt)

            trip_dao.delete(TRIP_ID)
            print(f"Deleted Trip: {TRIP_ID}")
        else:
            print(f"Trip {TRIP_ID} not found.")

        # 4. Delete Users
        user_dao = SqlAlchemyUserDao(session)
        
        if user_dao.find_by_id(USER1_ID):
            user_dao.delete(USER1_ID)
            print(f"Deleted User: {USER1_ID}")
        else:
            print(f"User {USER1_ID} not found.")

        if user_dao.find_by_id(USER2_ID):
            user_dao.delete(USER2_ID)
            print(f"Deleted User: {USER2_ID}")
        else:
            print(f"User {USER2_ID} not found.")

        session.commit()
        print("Data deletion completed successfully.")

    except Exception as e:
        session.rollback()
        print(f"Error deleting data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    delete_data()
