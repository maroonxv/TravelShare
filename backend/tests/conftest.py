import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from shared.database.core import Base

# Import all POs to ensure tables are registered
from app_auth.infrastructure.database.persistent_model.user_po import UserPO
from app_social.infrastructure.database.persistent_model.post_po import PostPO, CommentPO, LikePO
from app_social.infrastructure.database.persistent_model.conversation_po import ConversationPO
from app_social.infrastructure.database.persistent_model.message_po import MessagePO
from app_travel.infrastructure.database.persistent_model.trip_po import TripPO, TripMemberPO, TripDayPO, ActivityPO

@pytest.fixture(scope="session")
def engine():
    # Use in-memory SQLite for speed and isolation
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine, tables):
    """Returns a sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    connection.close()
