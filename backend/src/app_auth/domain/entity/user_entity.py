from app_auth.domain.value_objects.user_value_objects import UserId, UserName, UserEmail, UserPassword, UserRole
from app_auth.domain.domain_event.user_password_changed_event import UserPasswordChangedEvent
from app_auth.domain.domain_service.password_encoder import PasswordEncoder

class User:
    def __init__(self, user_id: UserId, user_name: UserName, user_email: UserEmail, user_password: UserPassword, user_role: UserRole) -> None:
        self.user_id = user_id
        self.user_name = user_name
        self.user_email = user_email
        self.user_password_hash = password_encoder.encode(user_password)
        self.user_role = user_role
        self.event_store = []


    def change_password(self, new_password: UserPassword) -> None:
        self.user_password_hash = password_encoder.encode(new_password)

        # 记录事件
        self.event_store.append(UserPasswordChangedEvent(
            user_id=self.user_id,
            user_name=self.user_name,
            user_email=self.user_email,
            user_role=self.user_role
        ))

    def change_user_name(self, new_user_name: UserName) -> None:
        self.user_name = new_user_name

    def change_user_email(self, new_user_email: UserEmail) -> None:
        self.user_email = new_user_email

    def change_user_role(self, new_user_role: UserRole) -> None:
        self.user_role = new_user_roles

    def is_admin(self) -> bool:
        return self.user_role == UserRole.ADMIN

    def is_password_correct(self, password: str, hasher: PasswordEncoder) -> bool:
        return hasher.verify(password, self.user_password_hash)

    
