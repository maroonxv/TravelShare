"""
旅行及相关持久化对象 (PO - Persistent Object)

用于 SQLAlchemy ORM 映射，与数据库表对应。
包含 TripPO, TripMemberPO, TripDayPO, ActivityPO, TransitPO。
"""
from datetime import datetime, date, time
from decimal import Decimal
from typing import List, Optional
import json

from sqlalchemy import Column, String, DateTime, Date, Time, Text, Boolean, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship
from shared.database.core import Base

from app_travel.domain.aggregate.trip_aggregate import Trip
from app_travel.domain.entity.trip_member import TripMember
from app_travel.domain.entity.trip_day_entity import TripDay
from app_travel.domain.entity.activity import Activity
from app_travel.domain.entity.transit import Transit
from app_travel.domain.value_objects.travel_value_objects import (
    TripId, TripName, TripDescription, DateRange, Money,
    TripStatus, TripVisibility, MemberRole, ActivityType, Location
)
from app_travel.domain.value_objects.transit_value_objects import (
    TransportMode, RouteInfo, TransitCost
)


class ActivityPO(Base):
    """活动持久化对象"""
    
    __tablename__ = 'activities'
    
    id = Column(String(36), primary_key=True)
    trip_day_id = Column(Integer, ForeignKey('trip_days.id'), nullable=False, index=True)
    
    name = Column(String(200), nullable=False)
    activity_type = Column(String(30), nullable=False)
    
    # 位置信息
    location_name = Column(String(200), nullable=False)
    location_latitude = Column(Numeric(10, 7), nullable=True)
    location_longitude = Column(Numeric(10, 7), nullable=True)
    location_address = Column(String(500), nullable=True)
    
    # 时间
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    # 费用
    cost_amount = Column(Numeric(10, 2), nullable=True)
    cost_currency = Column(String(3), nullable=True, default='CNY')
    
    notes = Column(Text, nullable=True)
    booking_reference = Column(String(100), nullable=True)
    
    # 关联
    trip_day = relationship('TripDayPO', back_populates='activities')
    
    def to_domain(self) -> Activity:
        """转换为领域实体"""
        location = Location(
            name=self.location_name,
            latitude=float(self.location_latitude) if self.location_latitude else None,
            longitude=float(self.location_longitude) if self.location_longitude else None,
            address=self.location_address
        )
        
        cost = None
        if self.cost_amount is not None:
            cost = Money(amount=self.cost_amount, currency=self.cost_currency or 'CNY')
        
        return Activity(
            id=self.id,
            name=self.name,
            activity_type=ActivityType.from_string(self.activity_type),
            location=location,
            start_time=self.start_time,
            end_time=self.end_time,
            cost=cost,
            notes=self.notes or '',
            booking_reference=self.booking_reference
        )
    
    @classmethod
    def from_domain(cls, activity: Activity, trip_day_id: int) -> 'ActivityPO':
        """从领域实体创建"""
        return cls(
            id=activity.id,
            trip_day_id=trip_day_id,
            name=activity.name,
            activity_type=activity.activity_type.value,
            location_name=activity.location.name,
            location_latitude=Decimal(str(activity.location.latitude)) if activity.location.latitude else None,
            location_longitude=Decimal(str(activity.location.longitude)) if activity.location.longitude else None,
            location_address=activity.location.address,
            start_time=activity.start_time,
            end_time=activity.end_time,
            cost_amount=activity.cost.amount if activity.cost else None,
            cost_currency=activity.cost.currency if activity.cost else None,
            notes=activity.notes,
            booking_reference=activity.booking_reference
        )


class TransitPO(Base):
    """交通持久化对象"""
    
    __tablename__ = 'transits'
    
    id = Column(String(36), primary_key=True)
    trip_day_id = Column(Integer, ForeignKey('trip_days.id'), nullable=False, index=True)
    
    from_activity_id = Column(String(36), nullable=False)
    to_activity_id = Column(String(36), nullable=False)
    transport_mode = Column(String(20), nullable=False)  # driving, walking, transit, cycling
    
    # 路线信息
    distance_meters = Column(Numeric(12, 2), nullable=False, default=0)
    duration_seconds = Column(Integer, nullable=False, default=0)
    polyline = Column(Text, nullable=True)
    
    # 时间
    departure_time = Column(Time, nullable=False)
    arrival_time = Column(Time, nullable=False)
    
    # 费用
    cost_amount = Column(Numeric(10, 2), nullable=True)
    cost_currency = Column(String(3), nullable=True, default='CNY')
    fuel_cost = Column(Numeric(10, 2), nullable=True)
    toll_cost = Column(Numeric(10, 2), nullable=True)
    ticket_cost = Column(Numeric(10, 2), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # 关联
    trip_day = relationship('TripDayPO', back_populates='transits')
    
    def to_domain(self) -> Transit:
        """转换为领域实体"""
        route_info = RouteInfo(
            distance_meters=float(self.distance_meters),
            duration_seconds=int(self.duration_seconds),
            polyline=self.polyline
        )
        
        # 构建 TransitCost
        estimated_cost = None
        if self.cost_amount is not None:
            estimated_money = Money(amount=self.cost_amount, currency=self.cost_currency or 'CNY')
            fuel_money = Money(amount=self.fuel_cost, currency='CNY') if self.fuel_cost else None
            toll_money = Money(amount=self.toll_cost, currency='CNY') if self.toll_cost else None
            ticket_money = Money(amount=self.ticket_cost, currency='CNY') if self.ticket_cost else None
            estimated_cost = TransitCost(
                estimated_cost=estimated_money,
                fuel_cost=fuel_money,
                toll_cost=toll_money,
                ticket_cost=ticket_money
            )
        
        return Transit(
            id=self.id,
            from_activity_id=self.from_activity_id,
            to_activity_id=self.to_activity_id,
            transport_mode=TransportMode.from_string(self.transport_mode),
            route_info=route_info,
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            estimated_cost=estimated_cost,
            notes=self.notes or ''
        )
    
    @classmethod
    def from_domain(cls, transit: Transit, trip_day_id: int) -> 'TransitPO':
        """从领域实体创建"""
        cost_amount = None
        fuel_cost = None
        toll_cost = None
        ticket_cost = None
        
        if transit.estimated_cost:
            cost_amount = transit.estimated_cost.estimated_cost.amount
            if transit.estimated_cost.fuel_cost:
                fuel_cost = transit.estimated_cost.fuel_cost.amount
            if transit.estimated_cost.toll_cost:
                toll_cost = transit.estimated_cost.toll_cost.amount
            if transit.estimated_cost.ticket_cost:
                ticket_cost = transit.estimated_cost.ticket_cost.amount
        
        return cls(
            id=transit.id,
            trip_day_id=trip_day_id,
            from_activity_id=transit.from_activity_id,
            to_activity_id=transit.to_activity_id,
            transport_mode=transit.transport_mode.value,
            distance_meters=Decimal(str(transit.route_info.distance_meters)),
            duration_seconds=transit.route_info.duration_seconds,
            polyline=transit.route_info.polyline,
            departure_time=transit.departure_time,
            arrival_time=transit.arrival_time,
            cost_amount=cost_amount,
            cost_currency='CNY',
            fuel_cost=fuel_cost,
            toll_cost=toll_cost,
            ticket_cost=ticket_cost,
            notes=transit.notes
        )


class TripDayPO(Base):
    """旅行日程持久化对象"""
    
    __tablename__ = 'trip_days'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(String(36), ForeignKey('trips.id'), nullable=False, index=True)
    
    day_number = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    theme = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # 关联
    trip = relationship('TripPO', back_populates='days')
    activities = relationship('ActivityPO', back_populates='trip_day', cascade='all, delete-orphan')
    transits = relationship('TransitPO', back_populates='trip_day', cascade='all, delete-orphan')
    
    def to_domain(self) -> TripDay:
        """转换为领域实体"""
        trip_day = TripDay(
            day_number=self.day_number,
            date=self.date,
            theme=self.theme,
            notes=self.notes or ''
        )
        # 添加活动
        for activity_po in self.activities:
            trip_day._activities.append(activity_po.to_domain())
        # 按时间排序
        trip_day._activities.sort(key=lambda a: a.start_time)
        
        # 添加交通
        for transit_po in self.transits:
            trip_day._transits.append(transit_po.to_domain())
        
        return trip_day
    
    @classmethod
    def from_domain(cls, trip_day: TripDay, trip_id: str) -> 'TripDayPO':
        """从领域实体创建"""
        po = cls(
            trip_id=trip_id,
            day_number=trip_day.day_number,
            date=trip_day.date,
            theme=trip_day.theme,
            notes=trip_day.notes
        )
        return po


class TripMemberPO(Base):
    """旅行成员持久化对象"""
    
    __tablename__ = 'trip_members'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(String(36), ForeignKey('trips.id'), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    
    role = Column(String(20), nullable=False, default='member')
    nickname = Column(String(50), nullable=True)
    joined_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关联
    trip = relationship('TripPO', back_populates='members')
    
    def to_domain(self) -> TripMember:
        """转换为领域实体"""
        return TripMember(
            user_id=self.user_id,
            role=MemberRole.from_string(self.role),
            joined_at=self.joined_at,
            nickname=self.nickname
        )
    
    @classmethod
    def from_domain(cls, member: TripMember, trip_id: str) -> 'TripMemberPO':
        """从领域实体创建"""
        return cls(
            trip_id=trip_id,
            user_id=member.user_id,
            role=member.role.value,
            nickname=member.nickname,
            joined_at=member.joined_at
        )


class TripPO(Base):
    """旅行持久化对象 - SQLAlchemy 模型"""
    
    __tablename__ = 'trips'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(String(36), nullable=False, index=True)
    
    # 日期范围
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # 预算
    budget_amount = Column(Numeric(10, 2), nullable=True)
    budget_currency = Column(String(3), nullable=True, default='CNY')
    
    # 状态
    visibility = Column(String(20), nullable=False, default='private')
    status = Column(String(20), nullable=False, default='planning')
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    members = relationship('TripMemberPO', back_populates='trip', cascade='all, delete-orphan')
    days = relationship('TripDayPO', back_populates='trip', cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f"TripPO(id={self.id}, name={self.name})"
    
    def to_domain(self) -> Trip:
        """将持久化对象转换为领域实体"""
        date_range = DateRange(
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        budget = None
        if self.budget_amount is not None:
            budget = Money(amount=self.budget_amount, currency=self.budget_currency or 'CNY')
        
        # 转换子实体
        domain_members = [m.to_domain() for m in self.members]
        domain_days = [d.to_domain() for d in sorted(self.days, key=lambda x: x.day_number)]
        
        return Trip.reconstitute(
            trip_id=TripId(self.id),
            name=TripName(self.name),
            description=TripDescription(self.description or ''),
            creator_id=self.creator_id,
            date_range=date_range,
            members=domain_members,
            days=domain_days,
            budget=budget,
            visibility=TripVisibility.from_string(self.visibility),
            status=TripStatus.from_string(self.status),
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    @classmethod
    def from_domain(cls, trip: Trip) -> 'TripPO':
        """从领域实体创建持久化对象"""
        po = cls(
            id=trip.id.value,
            name=trip.name.value,
            description=trip.description.value,
            creator_id=trip.creator_id,
            start_date=trip.date_range.start_date,
            end_date=trip.date_range.end_date,
            budget_amount=trip.budget.amount if trip.budget else None,
            budget_currency=trip.budget.currency if trip.budget else None,
            visibility=trip.visibility.value,
            status=trip.status.value,
            created_at=trip.created_at,
            updated_at=trip.updated_at
        )
        
        # 成员
        po.members = [TripMemberPO.from_domain(m, trip.id.value) for m in trip.members]
        
        # 日程和活动
        for day in trip.days:
            day_po = TripDayPO.from_domain(day, trip.id.value)
            day_po.activities = [ActivityPO.from_domain(a, day_po.id) for a in day.activities]
            day_po.transits = [TransitPO.from_domain(t, day_po.id) for t in day.transits]
            po.days.append(day_po)
        
        return po
    
    def update_from_domain(self, trip: Trip) -> None:
        """从领域实体更新持久化对象"""
        self.name = trip.name.value
        self.description = trip.description.value
        self.start_date = trip.date_range.start_date
        self.end_date = trip.date_range.end_date
        self.budget_amount = trip.budget.amount if trip.budget else None
        self.budget_currency = trip.budget.currency if trip.budget else None
        self.visibility = trip.visibility.value
        self.status = trip.status.value
        self.updated_at = trip.updated_at
