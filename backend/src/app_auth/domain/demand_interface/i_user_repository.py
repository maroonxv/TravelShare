
class IUserRepository:
    def add_user(self, user: User) -> None:
        pass
    
    def get_user_by_id(self, user_id: UserId) -> User:
        pass

    def get_user_by_name(self, user_name: UserName) -> User:
        pass

    def get_user_by_email(self, user_email: UserEmail) -> User:
        pass

    def update_user(self, user: User) -> None:
        pass

    def delete_user(self, user_id: UserId) -> None:
        pass

    def get_all_users(self) -> List[User]:
        pass

    def get_user_by_role(self, user_role: UserRole) -> List[User]:
        pass

    def get_user_by_name(self, user_name: UserName) -> User:
        pass

