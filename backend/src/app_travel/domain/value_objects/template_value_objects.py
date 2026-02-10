"""
Template value objects for trip templates
"""
from dataclasses import dataclass
from typing import Optional, Tuple
import uuid


@dataclass(frozen=True)
class TemplateId:
    """Template unique identifier"""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("TemplateId cannot be empty")
    
    @classmethod
    def generate(cls) -> 'TemplateId':
        return cls(str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TemplateActivityData:
    """Sanitized activity data for templates"""
    name: str
    activity_type: str
    location_name: str
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[str]
    duration_minutes: int
    cost_amount: Optional[float]
    cost_currency: str
    notes: str  # Public notes only (sanitized)
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Activity name cannot be empty")
        if self.duration_minutes < 0:
            raise ValueError("Duration cannot be negative")


@dataclass(frozen=True)
class TemplateDayData:
    """Sanitized day data for templates"""
    day_number: int
    theme: Optional[str]
    activities: Tuple[TemplateActivityData, ...]
    
    def __post_init__(self):
        if self.day_number < 1:
            raise ValueError("Day number must be positive")
        if not isinstance(self.activities, tuple):
            object.__setattr__(self, 'activities', tuple(self.activities))
