import sys
import os
from datetime import date, time
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from app_ai.infrastructure.retriever.sqlalchemy_mysql_retriever import SqlAlchemyMysqlRetriever
from app_travel.infrastructure.database.persistent_model.trip_po import ActivityPO, TripPO, TripDayPO
from app_social.infrastructure.database.persistent_model.post_po import PostPO
from app_travel.domain.value_objects.travel_value_objects import ActivityType


class TestSqlAlchemyMysqlRetrieverIntegration:
    @pytest.fixture
    def retriever(self, db_session):
        return SqlAlchemyMysqlRetriever(db_session)

    def test_jieba_search_engine_mode_improves_chinese_search(self, db_session, retriever):
        trip = TripPO(
            id="test_trip_1",
            name="北京旅行",
            description="清华一日游",
            creator_id="test_user_1",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1),
            visibility="public",
            status="planning",
        )
        db_session.add(trip)
        db_session.flush()

        trip_day = TripDayPO(
            trip_id=trip.id,
            day_number=1,
            date=date(2024, 1, 1),
        )
        db_session.add(trip_day)
        db_session.flush()

        activity = ActivityPO(
            id="test_activity_1",
            trip_day_id=trip_day.id,
            name="清华观光",
            activity_type=ActivityType.SIGHTSEEING.value,
            location_name="清华大学",
            start_time=time(9, 0),
            end_time=time(10, 0),
        )
        db_session.add(activity)

        post = PostPO(
            id="test_post_1",
            author_id="test_user_1",
            title="清华游记",
            text="我来到清华大学参观",
            visibility="public",
            is_deleted=False,
        )
        db_session.add(post)
        db_session.commit()

        results = retriever.search("北京清华大学")

        assert any(d.source_type == "trip" and d.reference_id == "test_trip_1" for d in results)
        assert any(d.source_type == "activity" and d.reference_id == "test_activity_1" for d in results)
        assert any(d.source_type == "post" and d.reference_id == "test_post_1" for d in results)

