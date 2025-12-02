

class AuthService:
    def __init__(self, user_repo: IUserRepository, password_encoder: IPasswordEncoder) -> None:
        self.user_repo = user_repo
        self.password_encoder = password_encoder

    
    def register_user(self, user_name: UserName, user_email: UserEmail, user_password: UserPassword, user_role: UserRole) -> None:
        if self.user_repo.exists_by_username(user_name):
            raise ValueError("Username already exists")
        if self.user_repo.exists_by_email(user_email):
            raise ValueError("Email already exists")
        
        user_id = UserId.generate()

        new_user = User(
            user_id=user_id,
            user_name=user_name,
            user_email=user_email,
            user_password_hash=self.password_encoder.encode(user_password),
            user_role=user_role
        )
        new_user.event_store.append(UserRegisteredEvent(
            user_id=user_id,
            user_name=user_name,
            user_email=user_email,
            user_role=user_role
        ))
        self.user_repo.add_user(new_user)

    def authenticate(self, email: UserEmail, password: UserPassword) -> bool:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("User not found")
        
        if self.password_encoder.verify(password, user.user_password_hash):
            user.event_store.append(UserLoggedInEvent(
                user_id=user.user_id,
                user_name=user.user_name,
                user_email=user.user_email,
                user_role=user.user_role
            ))
            return user
        else:
            return None

    def change_password(self, user_id: UserId, new_password: UserPassword) -> None:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if user.user_role == UserRole.ADMIN:
            raise ValueError("Admin password cannot be changed")
        
        # TODO: 增加邮箱验证码验证

        if self.password_encoder.verify(new_password, user.user_password_hash):
            raise ValueError("New password cannot be the same as the old password")

        user.change_password(new_password)
        user.event_store.append(UserPasswordChangedEvent(
            user_id=user.user_id,
            user_name=user.user_name,
            user_email=user.user_email,
            user_role=user.user_role
        ))
