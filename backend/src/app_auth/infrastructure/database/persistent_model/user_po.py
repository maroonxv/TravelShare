

class UserPO:
    def __init__(self, user_id: str, user_name: str, user_email: str, user_password: str, user_role: UserRole) -> None:
        self.user_id = user_id
        self.user_name = user_name
        self.user_email = user_email
        self.user_password = user_password
        self.user_role = user_role