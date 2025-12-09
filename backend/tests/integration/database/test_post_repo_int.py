import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))
import uuid
from datetime import datetime
from app_social.domain.aggregate.post_aggregate import Post
from app_social.domain.entity.comment_entity import Comment
from app_social.domain.value_objects.social_value_objects import PostId, PostContent, PostVisibility
from app_social.infrastructure.database.dao_impl.sqlalchemy_post_dao import SqlAlchemyPostDao
from app_social.infrastructure.database.repository_impl.post_repository_impl import PostRepositoryImpl

class TestPostRepositoryIntegration:
    
    @pytest.fixture
    def post_repo(self, integration_db_session):
        post_dao = SqlAlchemyPostDao(integration_db_session)
        return PostRepositoryImpl(post_dao)

    def test_save_full_aggregate(self, post_repo):
        # Arrange
        post_id = str(uuid.uuid4())
        author_id = str(uuid.uuid4())
        
        content = PostContent(
            title="Integration Post",
            text="Testing with MySQL",
            images=("img1.jpg",),
            tags=("python", "mysql")
        )
        
        post = Post.reconstitute(
            post_id=PostId(post_id),
            author_id=author_id,
            content=content,
            comments=[],
            likes=[],
            visibility=PostVisibility.PUBLIC,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_deleted=False
        )
        
        # Add a comment
        # Use domain method to add comment, which handles creation
        post.add_comment(commenter_id="commenter_1", content="Great post!")

        # Act
        post_repo.save(post)

        # Assert
        found_post = post_repo.find_by_id(PostId(post_id))
        assert found_post is not None
        assert found_post.content.title == "Integration Post"
        assert found_post.content.text == "Testing with MySQL"
        assert len(found_post.comments) == 1
        assert found_post.comments[0].content == "Great post!"
        assert found_post.comments[0].author_id == "commenter_1"
        assert "python" in found_post.content.tags

    def test_find_public_feed(self, post_repo):
        # Arrange
        p1_id = str(uuid.uuid4())
        p1 = Post.reconstitute(
            post_id=PostId(p1_id),
            author_id="u1",
            content=PostContent(title="P1", text="T1", tags=("fun",)),
            comments=[], likes=[], visibility=PostVisibility.PUBLIC,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow(), is_deleted=False
        )
        
        p2_id = str(uuid.uuid4())
        p2 = Post.reconstitute(
            post_id=PostId(p2_id),
            author_id="u1",
            content=PostContent(title="P2", text="T2", tags=("work",)),
            comments=[], likes=[], visibility=PostVisibility.PRIVATE,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow(), is_deleted=False
        )
        
        post_repo.save(p1)
        post_repo.save(p2)

        # Act
        feed = post_repo.find_public_feed(tags=["fun"])

        # Assert
        # Note: Integration DB might have other data, so we check if p1 is present
        found_ids = [p.id.value for p in feed]
        assert p1_id in found_ids
        assert p2_id not in found_ids

    def test_delete_post(self, post_repo):
        # Arrange
        post_id = str(uuid.uuid4())
        post = Post.reconstitute(
            post_id=PostId(post_id),
            author_id="u_del",
            content=PostContent(title="Del", text="Del", tags=()),
            comments=[], likes=[], visibility=PostVisibility.PUBLIC,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow(), is_deleted=False
        )
        post_repo.save(post)
        assert post_repo.find_by_id(post.id) is not None

        # Act
        post_repo.delete(post.id)

        # Assert
        assert post_repo.find_by_id(post.id) is None

    def test_find_by_author_pagination(self, post_repo):
        # Arrange
        author_id = str(uuid.uuid4())
        posts = []
        for i in range(3):
            p = Post.reconstitute(
                post_id=PostId(str(uuid.uuid4())),
                author_id=author_id,
                content=PostContent(title=f"Auth {i}", text="T", tags=()),
                comments=[], likes=[], visibility=PostVisibility.PUBLIC,
                created_at=datetime.utcnow(), updated_at=datetime.utcnow(), is_deleted=False
            )
            post_repo.save(p)
            posts.append(p)
        
        # Add deleted post
        deleted_post = Post.reconstitute(
            post_id=PostId(str(uuid.uuid4())),
            author_id=author_id,
            content=PostContent(title="Deleted", text="T", tags=()),
            comments=[], likes=[], visibility=PostVisibility.PUBLIC,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow(), is_deleted=True
        )
        post_repo.save(deleted_post)

        # Act
        # Default (no deleted)
        found_active = post_repo.find_by_author(author_id, include_deleted=False, limit=100)
        assert len(found_active) >= 3
        active_ids = [p.id.value for p in found_active]
        assert deleted_post.id.value not in active_ids
        
        # With deleted
        found_all = post_repo.find_by_author(author_id, include_deleted=True, limit=100)
        all_ids = [p.id.value for p in found_all]
        assert deleted_post.id.value in all_ids
        
        # Pagination
        page1 = post_repo.find_by_author(author_id, limit=1, offset=0)
        assert len(page1) == 1

    def test_find_by_visibility(self, post_repo):
        # Arrange
        p_pub = Post.reconstitute(
            post_id=PostId(str(uuid.uuid4())),
            author_id="u_vis",
            content=PostContent(title="Pub", text="T", tags=()),
            comments=[], likes=[], visibility=PostVisibility.PUBLIC,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow(), is_deleted=False
        )
        p_priv = Post.reconstitute(
            post_id=PostId(str(uuid.uuid4())),
            author_id="u_vis",
            content=PostContent(title="Priv", text="T", tags=()),
            comments=[], likes=[], visibility=PostVisibility.PRIVATE,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow(), is_deleted=False
        )
        post_repo.save(p_pub)
        post_repo.save(p_priv)

        # Act
        public_posts = post_repo.find_by_visibility(PostVisibility.PUBLIC, limit=100)
        private_posts = post_repo.find_by_visibility(PostVisibility.PRIVATE, limit=100)

        # Assert
        pub_ids = [p.id.value for p in public_posts]
        priv_ids = [p.id.value for p in private_posts]
        
        assert p_pub.id.value in pub_ids
        assert p_priv.id.value not in pub_ids
        
        assert p_priv.id.value in priv_ids
        assert p_pub.id.value not in priv_ids

    def test_count_by_author(self, post_repo):
        # Arrange
        author_id = str(uuid.uuid4())
        # Create 2 active, 1 deleted
        for i in range(2):
            p = Post.reconstitute(
                post_id=PostId(str(uuid.uuid4())),
                author_id=author_id,
                content=PostContent(title=f"Cnt {i}", text="T", tags=()),
                comments=[], likes=[], visibility=PostVisibility.PUBLIC,
                created_at=datetime.utcnow(), updated_at=datetime.utcnow(), is_deleted=False
            )
            post_repo.save(p)
            
        p_del = Post.reconstitute(
            post_id=PostId(str(uuid.uuid4())),
            author_id=author_id,
            content=PostContent(title="Del", text="T", tags=()),
            comments=[], likes=[], visibility=PostVisibility.PUBLIC,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow(), is_deleted=True
        )
        post_repo.save(p_del)

        # Act & Assert
        count_active = post_repo.count_by_author(author_id, include_deleted=False)
        assert count_active == 2
        
        count_all = post_repo.count_by_author(author_id, include_deleted=True)
        assert count_all == 3

    def test_find_by_trip(self, post_repo):
        # Arrange
        trip_id = str(uuid.uuid4())
        post = Post.reconstitute(
            post_id=PostId(str(uuid.uuid4())),
            author_id="u_trip",
            content=PostContent(title="Trip Post", text="T", tags=()),
            comments=[], likes=[], visibility=PostVisibility.PUBLIC,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow(), is_deleted=False,
            trip_id=trip_id
        )
        post_repo.save(post)

        # Act
        found = post_repo.find_by_trip(trip_id)

        # Assert
        assert found is not None
        assert found.id.value == post.id.value
        assert found.trip_id == trip_id
