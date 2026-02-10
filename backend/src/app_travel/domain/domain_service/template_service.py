"""
Template domain service

Handles template creation from trips and cloning templates to new trips.
"""
from datetime import date, timedelta, time
from typing import List, Optional
from app_travel.domain.aggregate.trip_aggregate import Trip
from app_travel.domain.aggregate.trip_template import TripTemplate
from app_travel.domain.value_objects.template_value_objects import (
    TemplateDayData, TemplateActivityData
)
from app_travel.domain.value_objects.travel_value_objects import (
    TripName, TripDescription, DateRange, TripStatus, TripVisibility,
    Location, Money, ActivityType
)
from app_travel.domain.entity.activity import Activity


class TemplateService:
    """Template domain service
    
    Provides methods for:
    1. Creating templates from completed public trips (with data sanitization)
    2. Cloning templates to new trips (with date adjustment)
    """
    
    @staticmethod
    def create_from_trip(trip: Trip, author_id: str) -> TripTemplate:
        """Create a template from a completed public trip
        
        Sanitizes personal data:
        - Strips member IDs
        - Removes booking references
        - Removes private notes
        
        Args:
            trip: Source trip (must be completed and public)
            author_id: Template author ID
            
        Returns:
            TripTemplate: New template
            
        Raises:
            ValueError: If trip is not completed or not public
        """
        # Validate trip status and visibility
        if trip.status != TripStatus.COMPLETED:
            raise ValueError("Only completed trips can be published as templates")
        
        if trip.visibility != TripVisibility.PUBLIC:
            raise ValueError("Only public trips can be published as templates")
        
        # Extract sanitized day data
        days_data: List[TemplateDayData] = []
        total_activity_count = 0
        
        for day in trip.days:
            activities_data: List[TemplateActivityData] = []
            
            for activity in day.activities:
                # Calculate duration from start and end time
                duration_minutes = activity.duration_minutes
                
                # Sanitize activity data
                activity_data = TemplateActivityData(
                    name=activity.name,
                    activity_type=activity.activity_type.value,
                    location_name=activity.location.name,
                    latitude=activity.location.latitude,
                    longitude=activity.location.longitude,
                    address=activity.location.address,
                    duration_minutes=duration_minutes,
                    cost_amount=float(activity.cost.amount) if activity.cost else None,
                    cost_currency=activity.cost.currency if activity.cost else "CNY",
                    notes=""  # Strip private notes
                )
                activities_data.append(activity_data)
                total_activity_count += 1
            
            day_data = TemplateDayData(
                day_number=day.day_number,
                theme=day.theme,
                activities=tuple(activities_data)
            )
            days_data.append(day_data)
        
        # Extract tags from trip name and description (simple implementation)
        # In a real system, this might use NLP or user-provided tags
        tags: List[str] = []
        
        # Create template
        template = TripTemplate.create(
            name=trip.name.value,
            description=trip.description.value,
            source_trip_id=trip.id.value,
            author_id=author_id,
            duration_days=trip.total_days,
            tags=tags,
            days_data=days_data,
            activity_count=total_activity_count
        )
        
        return template
    
    @staticmethod
    def clone_to_trip(
        template: TripTemplate,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> Trip:
        """Clone a template to a new trip
        
        Adjusts the number of days based on the provided date range:
        - If new_days == template_days: Direct mapping
        - If new_days > template_days: Extra days are empty
        - If new_days < template_days: Only use first new_days of template
        
        Args:
            template: Source template
            user_id: New trip creator ID
            start_date: New trip start date
            end_date: New trip end date
            
        Returns:
            Trip: New trip with cloned structure
            
        Raises:
            ValueError: If date range is invalid
        """
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")
        
        # Calculate new trip duration
        new_days = (end_date - start_date).days + 1
        
        # Create new trip
        trip = Trip.create(
            name=TripName(template.name),
            description=TripDescription(template.description),
            creator_id=user_id,
            date_range=DateRange(start_date, end_date),
            visibility=TripVisibility.PRIVATE
        )
        
        # Clone activities from template
        days_to_clone = min(new_days, template.duration_days)
        
        for i in range(days_to_clone):
            if i < len(template.days_data):
                template_day = template.days_data[i]
                trip_day = trip.get_day(i)
                
                if trip_day:
                    # Update theme
                    if template_day.theme:
                        trip_day.update_theme(template_day.theme)
                    
                    # Clone activities
                    for template_activity in template_day.activities:
                        # Calculate start and end times
                        # For simplicity, we'll use a default time distribution
                        # In a real system, this would preserve relative times
                        start_time = time(9, 0)  # Default start time
                        
                        # Calculate end time based on duration
                        total_minutes = template_activity.duration_minutes
                        hours = total_minutes // 60
                        minutes = total_minutes % 60
                        end_hour = start_time.hour + hours
                        end_minute = start_time.minute + minutes
                        
                        # Handle minute overflow
                        if end_minute >= 60:
                            end_hour += end_minute // 60
                            end_minute = end_minute % 60
                        
                        # Cap at 23:59
                        if end_hour >= 24:
                            end_hour = 23
                            end_minute = 59
                        
                        end_time = time(end_hour, end_minute)
                        
                        # Create activity
                        activity = Activity.create(
                            name=template_activity.name,
                            activity_type=ActivityType.from_string(template_activity.activity_type),
                            location=Location(
                                name=template_activity.location_name,
                                latitude=template_activity.latitude,
                                longitude=template_activity.longitude,
                                address=template_activity.address
                            ),
                            start_time=start_time,
                            end_time=end_time,
                            cost=Money(
                                amount=template_activity.cost_amount,
                                currency=template_activity.cost_currency
                            ) if template_activity.cost_amount else None,
                            notes=template_activity.notes
                        )
                        
                        # Add activity to trip day
                        trip_day.add_activity(activity)
        
        # Remaining days (if new_days > template_days) are left empty
        
        return trip
    
    @staticmethod
    def clone_trip_directly(
        source_trip: Trip,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> Trip:
        """Clone a public trip directly without creating a template
        
        Uses the same logic as template cloning.
        
        Args:
            source_trip: Source trip (must be public)
            user_id: New trip creator ID
            start_date: New trip start date
            end_date: New trip end date
            
        Returns:
            Trip: New trip with cloned structure
            
        Raises:
            ValueError: If source trip is not public or date range is invalid
        """
        if source_trip.visibility != TripVisibility.PUBLIC:
            raise ValueError("Can only clone public trips")
        
        # Create temporary template
        template = TemplateService.create_from_trip(source_trip, source_trip.creator_id)
        
        # Clone from template
        return TemplateService.clone_to_trip(template, user_id, start_date, end_date)
