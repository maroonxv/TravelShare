from app_auth.domain.value_objects.user_value_objects import UserName, UserEmail


class IUserUniquenessChecker:
    def is_user_name_unique(self, user_name: UserName) -> bool:
        pass
    
    def is_user_email_unique(self, user_email: UserEmail) -> bool:
        pass