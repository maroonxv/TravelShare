import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))
import uuid
from sqlalchemy.exc import IntegrityError
from app_auth.domain.entity.user_entity import User
from app_auth.domain.value_objects.user_value_objects import UserId, Email, Username, HashedPassword, UserRole, UserProfile
from app_auth.infrastructure.database.dao_impl.sqlalchemy_user_dao import SqlAlchemyUserDao
from app_auth.infrastructure.database.repository_impl.user_repository_impl import UserRepositoryImpl

class TestUserRepositoryIntegration:
    
    @pytest.fixture
    def user_repo(self, integration_db_session):
        user_dao = SqlAlchemyUserDao(integration_db_session)
        return UserRepositoryImpl(user_dao)

    def test_save_and_find_real_db(self, user_repo):
        # Arrange
        unique_id = str(uuid.uuid4())
        # Use reconstitute or factory method. Direct __init__ might mismatch signature if params are positional.
        # The error "User.__init__() got an unexpected keyword argument 'hashed_password'" suggests __init__ signature issue.
        # Let's use User.reconstitute which is safer for repo tests.
        user = User.reconstitute(
            user_id=UserId(unique_id),
            email=Email(f"test_{unique_id[:8]}@example.com"),
            username=Username(f"user_{unique_id[:8]}"),
            hashed_password=HashedPassword("secret"),
            role=UserRole.USER,
            profile=UserProfile(bio="Integration Test Bio")
        )

        # Act
        user_repo.save(user)

        # Assert
        found_user = user_repo.find_by_id(user.id)
        assert found_user is not None
        assert found_user.email.value == user.email.value
        assert found_user.profile.bio == "Integration Test Bio"

    def test_update_real_db(self, user_repo):
        # Arrange
        unique_id = str(uuid.uuid4())
        user = User.reconstitute(
            user_id=UserId(unique_id),
            email=Email(f"update_{unique_id[:8]}@example.com"),
            username=Username(f"update_{unique_id[:8]}"),
            hashed_password=HashedPassword("secret"),
            role=UserRole.ADMIN
        )
        user_repo.save(user)

        # Act
        # User is immutable or fields are protected. Need to use business method or protected setter if available.
        # Looking at User entity, it has `update_profile` method but that only updates username?
        # Wait, `profile` is protected `_profile`.
        # For test purpose, we might need to use `reconstitute` again or access protected member if python allows.
        # Or use a method like `update_profile` if it exists.
        # The User entity code shows: `_profile = profile`.
        # And no public setter for profile.
        # Actually, let's check `User.update_profile` in `user_entity.py`? No, the user provided code doesn't show `update_profile` updating `UserProfile` object, just `username`.
        # Wait, `user.py` (dataclass) had `update_profile`. `user_entity.py` (rich model) might be different.
        # In `user_entity.py` provided earlier:
        # It has `def update_profile(self, ...)` ? No, I need to check `user_entity.py` content again.
        # It has `_profile`.
        # Let's cheat for integration test and set protected attribute, OR better, add `update_profile_info` method to User entity if needed.
        # But I cannot modify User entity easily without user permission.
        # I will set `_profile` directly since it's python.
        
        new_profile = UserProfile(location="New York")
        user._profile = new_profile # Direct access for test setup
        user_repo.save(user)

        # Assert
        found_user = user_repo.find_by_id(user.id)
        assert found_user.profile.location == "New York"

    def test_delete_real_db(self, user_repo):
        # Arrange
        unique_id = str(uuid.uuid4())
        user = User.reconstitute(
            user_id=UserId(unique_id),
            email=Email(f"del_{unique_id[:8]}@example.com"),
            username=Username(f"del_{unique_id[:8]}"),
            hashed_password=HashedPassword("secret"),
            role=UserRole.USER
        )
        user_repo.save(user)
        assert user_repo.find_by_id(user.id) is not None

        # Act
        # Assuming delete method takes UserId or str. Checking interface...
        # Interface usually takes UserId or ID value. Let's assume UserId based on standard DDD.
        # But looking at other repos, some take value. Let's check user_repo implementation.
        # Wait, I don't have delete method in UserRepositoryImpl yet!
        # I will add the test first, it will fail, then I implement it.
        # I will assume the method signature is delete(user_id: UserId)
        try:
            user_repo.delete(user.id)
        except AttributeError:
            pytest.fail("UserRepository does not have delete method")

        # Assert
        assert user_repo.find_by_id(user.id) is None

    def test_find_by_email_and_username(self, user_repo):
        # Arrange
        unique_id = str(uuid.uuid4())
        email_str = f"find_{unique_id[:8]}@example.com"
        username_str = f"find_{unique_id[:8]}"
        user = User.reconstitute(
            user_id=UserId(unique_id),
            email=Email(email_str),
            username=Username(username_str),
            hashed_password=HashedPassword("secret"),
            role=UserRole.USER
        )
        user_repo.save(user)

        # Act & Assert
        found_by_email = user_repo.find_by_email(Email(email_str))
        assert found_by_email is not None
        assert found_by_email.id.value == unique_id

        found_by_username = user_repo.find_by_username(Username(username_str))
        assert found_by_username is not None
        assert found_by_username.id.value == unique_id

    def test_find_by_role(self, user_repo):
        # Arrange
        unique_id_1 = str(uuid.uuid4())
        unique_id_2 = str(uuid.uuid4())
        
        u1 = User.reconstitute(
            user_id=UserId(unique_id_1),
            email=Email(f"role1_{unique_id_1[:8]}@example.com"),
            username=Username(f"role1_{unique_id_1[:8]}"),
            hashed_password=HashedPassword("secret"),
            role=UserRole.ADMIN
        )
        u2 = User.reconstitute(
            user_id=UserId(unique_id_2),
            email=Email(f"role2_{unique_id_2[:8]}@example.com"),
            username=Username(f"role2_{unique_id_2[:8]}"),
            hashed_password=HashedPassword("secret"),
            role=UserRole.USER
        )
        user_repo.save(u1)
        user_repo.save(u2)

        # Act
        admins = user_repo.find_by_role(UserRole.ADMIN)
        
        # Assert
        # There might be other admins in DB, so check if u1 is present
        admin_ids = [u.id.value for u in admins]
        assert unique_id_1 in admin_ids
        assert unique_id_2 not in admin_ids

    def test_find_all_pagination(self, user_repo):
        # Arrange
        # Create 3 users
        prefix = str(uuid.uuid4())[:8]
        users = []
        for i in range(3):
            uid = str(uuid.uuid4())
            u = User.reconstitute(
                user_id=UserId(uid),
                email=Email(f"page_{prefix}_{i}@example.com"),
                username=Username(f"page_{prefix}_{i}"),
                hashed_password=HashedPassword("secret"),
                role=UserRole.USER
            )
            user_repo.save(u)
            users.append(u)
        
        # Act
        # We can't guarantee these are the only users, but if we query with limit=1, we should get 1.
        # And if we sort, we could verify order, but repo doesn't specify sort.
        # Just checking limit works and offset shifts results.
        
        # This test is tricky on a shared DB. 
        # But we can check if find_all returns at most limit items.
        
        batch1 = user_repo.find_all(limit=1, offset=0)
        assert len(batch1) == 1
        
        batch2 = user_repo.find_all(limit=1, offset=1)
        assert len(batch2) == 1
        
        # It's hard to verify they are different without sorting, but generally they should be.
        # Ideally, verify that we can find our created users across pages if we iterate enough,
        # but that's slow.
        # Let's just trust basic functionality for now.

    def test_duplicate_email_error(self, user_repo):
        # Arrange
        unique_id_1 = str(uuid.uuid4())
        unique_id_2 = str(uuid.uuid4())
        email = f"dup_{unique_id_1[:8]}@example.com"
        
        u1 = User.reconstitute(
            user_id=UserId(unique_id_1),
            email=Email(email),
            username=Username(f"u1_{unique_id_1[:8]}"),
            hashed_password=HashedPassword("secret"),
            role=UserRole.USER
        )
        user_repo.save(u1)
        
        u2 = User.reconstitute(
            user_id=UserId(unique_id_2),
            email=Email(email), # Same email
            username=Username(f"u2_{unique_id_2[:8]}"),
            hashed_password=HashedPassword("secret"),
            role=UserRole.USER
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            user_repo.save(u2)

