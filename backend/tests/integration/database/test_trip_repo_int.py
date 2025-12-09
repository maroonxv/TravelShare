import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))
import uuid
from datetime import date, datetime
from app_travel.domain.aggregate.trip_aggregate import Trip
from app_travel.domain.entity.trip_member import TripMember
from app_travel.domain.entity.trip_day_entity import TripDay
from app_travel.domain.value_objects.travel_value_objects import (
    TripId, TripName, TripDescription, DateRange, TripStatus, TripVisibility, MemberRole
)
from app_travel.infrastructure.database.dao_impl.sqlalchemy_trip_dao import SqlAlchemyTripDao
from app_travel.infrastructure.database.repository_impl.trip_repository_impl import TripRepositoryImpl

class TestTripRepositoryIntegration:
    
    @pytest.fixture
    def trip_repo(self, integration_db_session):
        trip_dao = SqlAlchemyTripDao(integration_db_session)
        return TripRepositoryImpl(trip_dao)

    def test_save_and_find_full_trip(self, trip_repo):
        # Arrange
        trip_id = str(uuid.uuid4())
        creator_id = str(uuid.uuid4())
        
        # Add day
        day = TripDay(day_number=1, date=date.today(), theme="Day 1")
        # trip.days returns a copy, so append won't work on it.
        # Since we are setting up via reconstitute (simulating existing state) or just testing save,
        # we can modify the internal list or pass it in reconstitute.
        # For this test, let's pass it in reconstitute to be clean.
        
        trip = Trip.reconstitute(
            trip_id=TripId(trip_id),
            name=TripName("Integration Trip"),
            description=TripDescription("Desc"),
            creator_id=creator_id,
            date_range=DateRange(date.today(), date.today()),
            members=[],
            days=[day],
            budget=None,
            visibility=TripVisibility.PUBLIC,
            status=TripStatus.PLANNING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add member
        member_id = creator_id[:36]
        trip.add_member(user_id=member_id, role=MemberRole.ADMIN, nickname="Creator")

        # Act
        trip_repo.save(trip)

        # Assert
        found = trip_repo.find_by_id(TripId(trip_id))
        assert found is not None
        assert found.name.value == "Integration Trip"
        assert len(found.members) == 1
        assert found.members[0].user_id == creator_id
        assert len(found.days) == 1
        assert found.days[0].theme == "Day 1"

    def test_find_by_member_integration(self, trip_repo):
        # Arrange
        t1_id = str(uuid.uuid4())
        user_id = "target_user"
        
        t1 = Trip.reconstitute(
            trip_id=TripId(t1_id),
            name=TripName("User's Trip"),
            description=TripDescription(""),
            creator_id=str(uuid.uuid4())[:36], # Ensure creator_id is within 36 chars
            date_range=DateRange(date.today(), date.today()),
            members=[], days=[], budget=None,
            visibility=TripVisibility.PUBLIC, status=TripStatus.PLANNING,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        t1.add_member(user_id=user_id, role=MemberRole.MEMBER, nickname="Member")
        
        trip_repo.save(t1)
        
        # Act
        trips = trip_repo.find_by_member(user_id)
        
        # Assert
        found_ids = [t.id.value for t in trips]
        assert t1_id in found_ids

    def test_delete_trip(self, trip_repo):
        # Arrange
        trip_id = str(uuid.uuid4())
        creator_id = str(uuid.uuid4())
        trip = Trip.reconstitute(
            trip_id=TripId(trip_id),
            name=TripName("To Delete"),
            description=TripDescription(""),
            creator_id=creator_id,
            date_range=DateRange(date.today(), date.today()),
            members=[], days=[], budget=None,
            visibility=TripVisibility.PUBLIC, status=TripStatus.PLANNING,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        trip_repo.save(trip)
        assert trip_repo.find_by_id(trip.id) is not None

        # Act
        trip_repo.delete(trip.id)

        # Assert
        assert trip_repo.find_by_id(trip.id) is None

    def test_find_by_creator(self, trip_repo):
        # Arrange
        creator_id = str(uuid.uuid4())[:36]
        other_creator = str(uuid.uuid4())[:36]
        
        t1 = Trip.reconstitute(
            trip_id=TripId(str(uuid.uuid4())),
            name=TripName("Creator Trip 1"),
            description=TripDescription(""),
            creator_id=creator_id,
            date_range=DateRange(date.today(), date.today()),
            members=[], days=[], budget=None,
            visibility=TripVisibility.PUBLIC, status=TripStatus.PLANNING,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        t2 = Trip.reconstitute(
            trip_id=TripId(str(uuid.uuid4())),
            name=TripName("Other Trip"),
            description=TripDescription(""),
            creator_id=other_creator,
            date_range=DateRange(date.today(), date.today()),
            members=[], days=[], budget=None,
            visibility=TripVisibility.PUBLIC, status=TripStatus.PLANNING,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        trip_repo.save(t1)
        trip_repo.save(t2)

        # Act
        found = trip_repo.find_by_creator(creator_id)

        # Assert
        found_ids = [t.id.value for t in found]
        assert t1.id.value in found_ids
        assert t2.id.value not in found_ids

    def test_find_public_pagination(self, trip_repo):
        # Arrange
        # Create 3 public trips
        prefix = str(uuid.uuid4())[:8]
        trips = []
        for i in range(3):
            t = Trip.reconstitute(
                trip_id=TripId(str(uuid.uuid4())),
                name=TripName(f"Public {prefix} {i}"),
                description=TripDescription(""),
                creator_id=str(uuid.uuid4())[:36],
                date_range=DateRange(date.today(), date.today()),
                members=[], days=[], budget=None,
                visibility=TripVisibility.PUBLIC, status=TripStatus.PLANNING,
                created_at=datetime.utcnow(), updated_at=datetime.utcnow()
            )
            trip_repo.save(t)
            trips.append(t)
            
        # Create 1 private trip
        private_t = Trip.reconstitute(
            trip_id=TripId(str(uuid.uuid4())),
            name=TripName(f"Private {prefix}"),
            description=TripDescription(""),
            creator_id=str(uuid.uuid4())[:36],
            date_range=DateRange(date.today(), date.today()),
            members=[], days=[], budget=None,
            visibility=TripVisibility.PRIVATE, status=TripStatus.PLANNING,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        trip_repo.save(private_t)

        # Act & Assert
        # Check pagination
        page1 = trip_repo.find_public(limit=1, offset=0)
        assert len(page1) == 1
        
        # Check that private trip is not returned
        # Fetch a large enough page to cover likely recent inserts
        # Or better, check specific IDs if we can, but find_public doesn't filter by other things easily.
        # But we can verify that returned trips are all public.
        
        public_trips = trip_repo.find_public(limit=100)
        for t in public_trips:
            assert t.visibility == TripVisibility.PUBLIC
            
        # Verify our private trip is NOT in the list
        public_ids = [t.id.value for t in public_trips]
        assert private_t.id.value not in public_ids
        
        # Verify at least one of our public trips is there
        # (Assuming test DB doesn't have thousands of recent trips pushing it off page 1)
        # Since we use a shared DB, we can't guarantee, but usually fine for integration tests.
        found_any = any(t.id.value in public_ids for t in trips)
        assert found_any

    def test_exists(self, trip_repo):
        # Arrange
        trip_id = str(uuid.uuid4())
        trip = Trip.reconstitute(
            trip_id=TripId(trip_id),
            name=TripName("Exists Check"),
            description=TripDescription(""),
            creator_id=str(uuid.uuid4())[:36],
            date_range=DateRange(date.today(), date.today()),
            members=[], days=[], budget=None,
            visibility=TripVisibility.PUBLIC, status=TripStatus.PLANNING,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        trip_repo.save(trip)

        # Act & Assert
        assert trip_repo.exists(TripId(trip_id))
        assert not trip_repo.exists(TripId(str(uuid.uuid4())))

