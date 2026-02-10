"""
TripTemplate aggregate root

Represents a reusable trip template created from completed public trips.
Contains sanitized trip structure without personal data.
"""
from datetime import datetime
from typing import List, Optional
from app_travel.domain.value_objects.template_value_objects import (
    TemplateId, TemplateDayData
)


class TripTemplate:
    """Trip template aggregate root
    
    A template is a sanitized version of a completed public trip that can be
    cloned by other users to create their own trips.
    """
    
    def __init__(
        self,
        template_id: TemplateId,
        name: str,
        description: str,
        source_trip_id: str,
        author_id: str,
        duration_days: int,
        tags: List[str],
        days_data: List[TemplateDayData],
        activity_count: int,
        created_at: Optional[datetime] = None
    ):
        self._id = template_id
        self._name = name
        self._description = description
        self._source_trip_id = source_trip_id
        self._author_id = author_id
        self._duration_days = duration_days
        self._tags = tags
        self._days_data = days_data
        self._activity_count = activity_count
        self._created_at = created_at or datetime.utcnow()
    
    # ==================== Factory Methods ====================
    
    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        source_trip_id: str,
        author_id: str,
        duration_days: int,
        tags: List[str],
        days_data: List[TemplateDayData],
        activity_count: int
    ) -> 'TripTemplate':
        """Create a new trip template"""
        if not name or not name.strip():
            raise ValueError("Template name cannot be empty")
        if duration_days < 1:
            raise ValueError("Duration must be at least 1 day")
        if activity_count < 0:
            raise ValueError("Activity count cannot be negative")
        
        return cls(
            template_id=TemplateId.generate(),
            name=name,
            description=description,
            source_trip_id=source_trip_id,
            author_id=author_id,
            duration_days=duration_days,
            tags=tags,
            days_data=days_data,
            activity_count=activity_count
        )
    
    @classmethod
    def reconstitute(
        cls,
        template_id: TemplateId,
        name: str,
        description: str,
        source_trip_id: str,
        author_id: str,
        duration_days: int,
        tags: List[str],
        days_data: List[TemplateDayData],
        activity_count: int,
        created_at: datetime
    ) -> 'TripTemplate':
        """Reconstitute template from persistence"""
        return cls(
            template_id=template_id,
            name=name,
            description=description,
            source_trip_id=source_trip_id,
            author_id=author_id,
            duration_days=duration_days,
            tags=tags,
            days_data=days_data,
            activity_count=activity_count,
            created_at=created_at
        )
    
    # ==================== Property Accessors ====================
    
    @property
    def id(self) -> TemplateId:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def source_trip_id(self) -> str:
        return self._source_trip_id
    
    @property
    def author_id(self) -> str:
        return self._author_id
    
    @property
    def duration_days(self) -> int:
        return self._duration_days
    
    @property
    def tags(self) -> List[str]:
        return self._tags.copy()
    
    @property
    def days_data(self) -> List[TemplateDayData]:
        return self._days_data.copy()
    
    @property
    def activity_count(self) -> int:
        return self._activity_count
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TripTemplate):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id.value)
    
    def __repr__(self) -> str:
        return f"TripTemplate(id={self._id.value}, name={self._name}, duration={self._duration_days})"
