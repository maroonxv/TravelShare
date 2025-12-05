import pytest
import json
from datetime import datetime
from app_social.infrastructure.database.persistent_model.post_po import PostPO
from app_social.infrastructure.database.dao_impl.sqlalchemy_post_dao import SqlAlchemyPostDao

class TestPostDao:
    
    @pytest.fixture
    def post_dao(self, db_session):
        return SqlAlchemyPostDao(db_session)

    def test_find_by_author(self, post_dao, db_session):
        p1 = PostPO(id="p1", author_id="u1", title="t1", text="txt", is_deleted=False)
        p2 = PostPO(id="p2", author_id="u1", title="t2", text="txt", is_deleted=True)
        p3 = PostPO(id="p3", author_id="u2", title="t3", text="txt", is_deleted=False)
        
        db_session.add_all([p1, p2, p3])
        db_session.flush()
        
        # Default: no deleted
        posts = post_dao.find_by_author("u1")
        assert len(posts) == 1
        assert posts[0].id == "p1"
        
        # Include deleted
        posts_all = post_dao.find_by_author("u1", include_deleted=True)
        assert len(posts_all) == 2

    def test_find_public_feed_tags(self, post_dao, db_session):
        # p1: public, tag A
        p1 = PostPO(id="p1", author_id="u", title="t", text="t", visibility="public", tags_json=json.dumps(["A"]))
        # p2: public, tag B
        p2 = PostPO(id="p2", author_id="u", title="t", text="t", visibility="public", tags_json=json.dumps(["B"]))
        # p3: private, tag A
        p3 = PostPO(id="p3", author_id="u", title="t", text="t", visibility="private", tags_json=json.dumps(["A"]))
        # p4: public, no tags
        p4 = PostPO(id="p4", author_id="u", title="t", text="t", visibility="public", tags_json=json.dumps([]))
        
        db_session.add_all([p1, p2, p3, p4])
        db_session.flush()
        
        # All public
        feed = post_dao.find_public_feed()
        assert len(feed) == 3 # p1, p2, p4
        
        # Filter by tag A
        feed_a = post_dao.find_public_feed(tags=["A"])
        assert len(feed_a) == 1
        assert feed_a[0].id == "p1"
        
        # Filter by tag A or B
        feed_ab = post_dao.find_public_feed(tags=["A", "B"])
        assert len(feed_ab) == 2

    def test_count_by_author(self, post_dao, db_session):
        p1 = PostPO(id="p1", author_id="u_count", title="t", text="t")
        p2 = PostPO(id="p2", author_id="u_count", title="t", text="t")
        post_dao.add(p1)
        post_dao.add(p2)
        
        assert post_dao.count_by_author("u_count") == 2
        assert post_dao.count_by_author("u_other") == 0

    def test_find_by_trip(self, post_dao, db_session):
        p = PostPO(id="p_trip", author_id="u", title="t", text="t", trip_id="trip_123")
        post_dao.add(p)
        
        found = post_dao.find_by_trip("trip_123")
        assert found is not None
        assert found.id == "p_trip"
