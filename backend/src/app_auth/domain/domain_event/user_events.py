from dataclasses import dataclass

@dataclass(frozen=True)
class UserRegisteredEvent:
    user_id: UserId
    user_name: UserName
    user_email: UserEmail
    user_role: UserRole


@dataclass(frozen=True)
class UserLoggedInEvent:
    user_id: UserId
    user_name: UserName
    user_email: UserEmail
    user_role: UserRole


@dataclass(frozen=True)
class UserLoggedOutEvent:
    user_id: UserId
    user_name: UserName
    user_email: UserEmail
    user_role: UserRole


@dataclass(frozen=True)
class UserPasswordChangedEvent:
    user_id: UserId
    user_name: UserName
    user_email: UserEmail
    user_role: UserRole