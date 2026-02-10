"""
Trip template persistent object (PO)

Used for SQLAlchemy ORM mapping to database tables.
"""
from datetime import datetime
from typing import List
import json

from sqlalchemy import Column, String, DateTime, Text, Integer
from shared.database.core import Base

from app_travel.domain.aggregate.trip_template import TripTemplate
from app_travel.domain.value_objects.template_value_objects import (
    TemplateId, TemplateDayData, TemplateActivityData
)


class TripTemplatePO(Base):
    """Trip template persistent object - SQLAlchemy model"""
    
    __tablename__ = 'trip_templates'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    source_trip_id = Column(String(36), nullable=False)
    author_id = Column(String(36), nullable=False, index=True)
    duration_days = Column(Integer, nullable=False)
    tags_json = Column(Text, nullable=True)
    days_data_json = Column(Text, nullable=False)
    activity_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self) -> str:
        return f"TripTemplatePO(id={self.id}, name={self.name})"
    
    def to_domain(self) -> TripTemplate:
        """Convert persistent object to domain entity"""
        # Parse tags
        tags = json.loads(self.tags_json) if self.tags_json else []
        
        # Parse days data
        days_data_list = json.loads(self.days_data_json)
        days_data: List[TemplateDayData] = []
        
        for day_dict in days_data_list:
            activities_data = []
            for activity_dict in day_dict['activities']:
                activity = TemplateActivityData(
                    name=activity_dict['name'],
                    activity_type=activity_dict['activity_type'],
                    location_name=activity_dict['location_name'],
                    latitude=activity_dict.get('latitude'),
                    longitude=activity_dict.get('longitude'),
                    address=activity_dict.get('address'),
                    duration_minutes=activity_dict['duration_minutes'],
                    cost_amount=activity_dict.get('cost_amount'),
                    cost_currency=activity_dict.get('cost_currency', 'CNY'),
                    notes=activity_dict.get('notes', '')
                )
                activities_data.append(activity)
            
            day_data = TemplateDayData(
                day_number=day_dict['day_number'],
                theme=day_dict.get('theme'),
                activities=tuple(activities_data)
            )
            days_data.append(day_data)
        
        return TripTemplate.reconstitute(
            template_id=TemplateId(self.id),
            name=self.name,
            description=self.description or '',
            source_trip_id=self.source_trip_id,
            author_id=self.author_id,
            duration_days=self.duration_days,
            tags=tags,
            days_data=days_data,
            activity_count=self.activity_count,
            created_at=self.created_at
        )
    
    @classmethod
    def from_domain(cls, template: TripTemplate) -> 'TripTemplatePO':
        """Create persistent object from domain entity"""
        # Serialize tags
        tags_json = json.dumps(template.tags)
        
        # Serialize days data
        days_data_list = []
        for day_data in template.days_data:
            activities_list = []
            for activity in day_data.activities:
                activity_dict = {
                    'name': activity.name,
                    'activity_type': activity.activity_type,
                    'location_name': activity.location_name,
                    'latitude': activity.latitude,
                    'longitude': activity.longitude,
                    'address': activity.address,
                    'duration_minutes': activity.duration_minutes,
                    'cost_amount': activity.cost_amount,
                    'cost_currency': activity.cost_currency,
                    'notes': activity.notes
                }
                activities_list.append(activity_dict)
            
            day_dict = {
                'day_number': day_data.day_number,
                'theme': day_data.theme,
                'activities': activities_list
            }
            days_data_list.append(day_dict)
        
        days_data_json = json.dumps(days_data_list)
        
        return cls(
            id=template.id.value,
            name=template.name,
            description=template.description,
            source_trip_id=template.source_trip_id,
            author_id=template.author_id,
            duration_days=template.duration_days,
            tags_json=tags_json,
            days_data_json=days_data_json,
            activity_count=template.activity_count,
            created_at=template.created_at
        )
