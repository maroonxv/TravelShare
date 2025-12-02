
class IUserDao:
    def find_user_by_id(self, user_id: UserId) -> User:
        pass

    def add_user(self, user: User) -> None:
        pass

    def update_user(self, user: User) -> None:
        pass

    def delete_user(self, user_id: UserId) -> None:
        pass