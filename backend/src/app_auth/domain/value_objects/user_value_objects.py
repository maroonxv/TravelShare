from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    value: str


@dataclass(frozen=True)
class UserName:
    value: str


@dataclass(frozen=True)
class UserEmail:
    value: str


@dataclass(frozen=True)
class UserPassword:
    value: str


@dataclass(frozen=True)
class UserRole:
    value: str