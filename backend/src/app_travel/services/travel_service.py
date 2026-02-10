"""
旅行应用服务 - 应用层

协调领域对象完成用例，管理事务边界，发布领域事件。
遵循 DDD 原则：应用层保持无状态，尽可能薄。
复杂业务逻辑由领域层（聚合根、领域服务）处理。
"""
from datetime import date, time
from typing import List, Optional, Dict, Any
from decimal import Decimal

from app_travel.domain.aggregate.trip_aggregate import Trip
from app_travel.domain.entity.activity import Activity
from app_travel.domain.demand_interface.i_trip_repository import ITripRepository
from app_travel.domain.demand_interface.i_geo_service import IGeoService
from app_travel.domain.domain_service.itinerary_service import ItineraryService
from app_travel.domain.value_objects.travel_value_objects import (
    TripId, TripName, TripDescription, DateRange, Money,
    TripStatus, TripVisibility, MemberRole, ActivityType, Location
)
from app_travel.domain.value_objects.itinerary_value_objects import TransitCalculationResult
from app_travel.domain.value_objects.trip_statistics import TripStatistics
from shared.event_bus import EventBus


class TravelService:
    """旅行应用服务
    
    职责：
    - 协调领域对象完成用例
    - 管理事务边界
    - 发布领域事件
    
    设计原则：
    - 无状态：不保存任何业务状态，所有状态由领域对象管理
    - 薄应用层：复杂逻辑委托给领域服务（ItineraryService）和聚合根（Trip）
    - 编排者：负责调用顺序和事件发布，不包含业务逻辑
    """
    
    def __init__(
        self,
        trip_repository: ITripRepository,
        geo_service: IGeoService,
        event_bus: Optional[EventBus] = None
    ):
        """初始化应用服务
        
        Args:
            trip_repository: 旅行仓库
            geo_service: 地理服务（用于创建 ItineraryService）
            event_bus: 事件总线（可选，默认使用全局实例）
        """
        self._trip_repository = trip_repository
        self._geo_service = geo_service
        self._event_bus = event_bus or EventBus.get_instance()
    
    def _create_itinerary_service(self) -> ItineraryService:
        """创建行程服务实例（无状态，每次调用创建新实例）"""
        return ItineraryService(self._geo_service)
    
    def _publish_events(self, trip: Trip) -> None:
        """发布聚合根中累积的领域事件"""
        events = trip.pop_events()
        self._event_bus.publish_all(events)
    
    # ==================== Trip CRUD ====================
    
    def create_trip(
        self,
        name: str,
        description: str,
        creator_id: str,
        start_date: date,
        end_date: date,
        budget_amount: Optional[float] = None,
        budget_currency: str = "CNY",
        visibility: str = "private",
        cover_image_url: Optional[str] = None
    ) -> Trip:
        """创建旅行
        
        Args:
            name: 旅行名称
            description: 旅行描述
            creator_id: 创建者ID
            start_date: 开始日期
            end_date: 结束日期
            budget_amount: 预算金额（可选）
            budget_currency: 预算货币（默认CNY）
            visibility: 可见性（默认private）
            cover_image_url: 封面图片URL（可选）
            
        Returns:
            创建的旅行实例
        """
        # 构建值对象
        trip_name = TripName(name)
        trip_desc = TripDescription(description)
        date_range = DateRange(start_date, end_date)
        budget = Money(Decimal(str(budget_amount)), budget_currency) if budget_amount else None
        trip_visibility = TripVisibility.from_string(visibility)
        
        # 通过工厂方法创建（领域逻辑在聚合根中）
        trip = Trip.create(
            name=trip_name,
            description=trip_desc,
            creator_id=creator_id,
            date_range=date_range,
            budget=budget,
            visibility=trip_visibility,
            cover_image_url=cover_image_url
        )
        
        # 持久化
        self._trip_repository.save(trip)
        
        # 发布事件
        self._publish_events(trip)
        
        return trip
    
    def get_trip(self, trip_id: str) -> Optional[Trip]:
        """获取旅行
        
        Args:
            trip_id: 旅行ID
            
        Returns:
            旅行实例，不存在返回 None
        """
        return self._trip_repository.find_by_id(TripId(trip_id))
    
    def update_trip(
        self,
        trip_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = None,
        budget_amount: Optional[float] = None,
        budget_currency: str = "CNY",
        status: Optional[str] = None,
        cover_image_url: Optional[str] = None
    ) -> Optional[Trip]:
        """更新旅行基本信息
        
        Args:
            trip_id: 旅行ID
            name: 新名称（可选）
            description: 新描述（可选）
            visibility: 新可见性（可选）
            budget_amount: 新预算金额（可选）
            budget_currency: 预算货币
            status: 新状态（可选）
            cover_image_url: 新封面图片URL（可选）
            
        Returns:
            更新后的旅行实例
        """
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
        
        # 委托给聚合根处理（领域逻辑在聚合根中）
        # 构建值对象
        trip_name = TripName(name) if name else None
        trip_desc = TripDescription(description) if description is not None else None
        trip_visibility = TripVisibility.from_string(visibility) if visibility else None
        
        budget = None
        if budget_amount is not None:
             budget = Money(Decimal(str(budget_amount)), budget_currency) if budget_amount > 0 else None
        
        # 调用聚合根的 update_info 方法
        # 注意：这里我们使用 update_info 来统一处理信息更新，而不是分散的 update_xxx
        # 之前的 update_name 等方法如果不再使用可以考虑移除或保留兼容
        
        # 为了兼容现有代码，我们先使用聚合根提供的具体方法，对于新加的 cover_image_url 和 visibility，
        # 如果聚合根有 update_info 最好用那个。
        # 查看 Trip 聚合根代码，它有 update_info 方法支持 name, description, budget, visibility, cover_image_url
        
        trip.update_info(
            name=trip_name,
            description=trip_desc,
            budget=budget,
            visibility=trip_visibility,
            cover_image_url=cover_image_url
        )
        
        if status:
            trip.update_status(TripStatus.from_string(status))
        
        # 持久化
        self._trip_repository.save(trip)
        
        # 发布事件
        self._publish_events(trip)
        
        return trip
    
    def delete_trip(self, trip_id: str) -> bool:
        """删除旅行
        
        Args:
            trip_id: 旅行ID
            
        Returns:
            是否成功删除
        """
        tid = TripId(trip_id)
        if not self._trip_repository.exists(tid):
            return False
        
        self._trip_repository.delete(tid)
        return True
    
    def list_user_trips(
        self, 
        user_id: str, 
        status: Optional[str] = None
    ) -> List[Trip]:
        """获取用户参与的旅行列表
        
        Args:
            user_id: 用户ID
            status: 状态筛选（可选）
            
        Returns:
            旅行列表
        """
        trip_status = TripStatus.from_string(status) if status else None
        return self._trip_repository.find_by_member(user_id, trip_status)
    
    def list_created_trips(self, creator_id: str) -> List[Trip]:
        """获取用户创建的旅行列表"""
        return self._trip_repository.find_by_creator(creator_id)
    
    def list_public_trips(self, limit: int = 20, offset: int = 0, search_query: Optional[str] = None) -> List[Trip]:
        """获取公开的旅行列表"""
        return self._trip_repository.find_public(limit, offset, search_query)
    
    # ==================== 成员管理 ====================
    
    def add_member(
        self,
        trip_id: str,
        user_id: str,
        role: str = "member",
        added_by: str = None
    ) -> Optional[Trip]:
        """添加成员
        
        Args:
            trip_id: 旅行ID
            user_id: 被添加用户ID
            role: 角色
            added_by: 操作者ID
        """
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
        
        # 检查是否为好友
        if added_by and added_by != user_id:
            try:
                from app_social.services.social_service import SocialService
                social_service = SocialService()
                if not social_service.are_friends(added_by, user_id):
                    raise ValueError(f"User {user_id} is not your friend")
            except ImportError:
                # 忽略循环依赖或模块未找到，降级处理
                pass
            except Exception as e:
                # 重新抛出业务异常
                raise e

        # 委托给聚合根（业务规则在聚合根中）
        trip.add_member(
            user_id=user_id,
            role=MemberRole.from_string(role),
            added_by=added_by
        )
        
        self._trip_repository.save(trip)
        self._publish_events(trip)
        
        return trip
    
    def remove_member(
        self,
        trip_id: str,
        user_id: str,
        removed_by: str,
        reason: Optional[str] = None
    ) -> Optional[Trip]:
        """移除成员"""
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
        
        trip.remove_member(user_id, removed_by, reason)
        
        self._trip_repository.save(trip)
        self._publish_events(trip)
        
        return trip
    
    def change_member_role(
        self,
        trip_id: str,
        user_id: str,
        new_role: str,
        changed_by: str
    ) -> Optional[Trip]:
        """更改成员角色"""
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
        
        trip.change_member_role(user_id, MemberRole.from_string(new_role), changed_by)
        
        self._trip_repository.save(trip)
        self._publish_events(trip)
        
        return trip
    
    # ==================== 活动与行程管理 ====================
    
    def add_activity(
        self,
        trip_id: str,
        day_index: int,
        operator_id: str,
        name: str,
        activity_type: str,
        location_name: str,
        start_time: time,
        end_time: time,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        address: Optional[str] = None,
        cost_amount: Optional[float] = None,
        cost_currency: str = "CNY",
        notes: str = ""
    ) -> Optional[TransitCalculationResult]:
        """添加活动到指定日期
        
        自动计算与前一个活动之间的交通。
        
        Returns:
            TransitCalculationResult 包含计算的交通和可能的警告
        """
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
        
        # Auto-geocode if coordinates are missing
        if (latitude is None or longitude is None) and (location_name or address):
            try:
                # Prioritize address, fallback to location_name
                query = address if address else location_name
                geo_loc = self._geo_service.geocode(query)
                if geo_loc:
                    latitude = geo_loc.latitude
                    longitude = geo_loc.longitude
                    # If address was missing, fill it from geocode result
                    if not address:
                        address = geo_loc.address
            except Exception as e:
                print(f"Auto-geocode failed for {location_name}: {e}")

        # 构建活动实体
        location = Location(
            name=location_name,
            latitude=latitude,
            longitude=longitude,
            address=address
        )
        cost = Money(Decimal(str(cost_amount)), cost_currency) if cost_amount else None
        
        activity = Activity.create(
            name=name,
            activity_type=ActivityType.from_string(activity_type),
            location=location,
            start_time=start_time,
            end_time=end_time,
            cost=cost,
            notes=notes
        )
        
        # 委托给聚合根，传入行程服务（无状态）
        itinerary_service = self._create_itinerary_service()
        result = trip.add_activity(day_index, activity, operator_id, itinerary_service)
        
        self._trip_repository.save(trip)
        self._publish_events(trip)
        
        return result or TransitCalculationResult()
    
    def modify_activity(
        self,
        trip_id: str,
        day_index: int,
        activity_id: str,
        operator_id: str,
        **updates
    ) -> Optional[TransitCalculationResult]:
        """修改活动
        
        修改后重新计算相邻的交通。
        
        Args:
            trip_id: 旅行ID
            day_index: 日期索引
            activity_id: 活动ID
            operator_id: 操作者ID
            **updates: 要更新的字段
        """
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
        
        # 处理特殊字段转换
        if 'location_name' in updates:
            loc_name = updates.pop('location_name')
            lat = updates.pop('latitude', None)
            lng = updates.pop('longitude', None)
            addr = updates.pop('address', None)

            # Auto-geocode if coordinates are missing
            if (lat is None or lng is None) and (loc_name or addr):
                try:
                    query = addr if addr else loc_name
                    geo_loc = self._geo_service.geocode(query)
                    if geo_loc:
                        lat = geo_loc.latitude
                        lng = geo_loc.longitude
                        if not addr:
                            addr = geo_loc.address
                except Exception as e:
                    print(f"Auto-geocode failed for {loc_name}: {e}")

            updates['location'] = Location(
                name=loc_name,
                latitude=lat,
                longitude=lng,
                address=addr
            )
        if 'activity_type' in updates:
            updates['activity_type'] = ActivityType.from_string(updates['activity_type'])
        if 'cost_amount' in updates:
            cost_amount = updates.pop('cost_amount')
            cost_currency = updates.pop('cost_currency', 'CNY')
            updates['cost'] = Money(Decimal(str(cost_amount)), cost_currency) if cost_amount else None
        
        # 委托给聚合根
        itinerary_service = self._create_itinerary_service()
        result = trip.modify_activity(day_index, activity_id, operator_id, itinerary_service, **updates)
        
        self._trip_repository.save(trip)
        self._publish_events(trip)
        
        return result or TransitCalculationResult()

    def modify_transit(
        self,
        trip_id: str,
        day_index: int,
        transit_id: str,
        operator_id: str,
        transport_mode: Optional[str] = None
    ) -> Optional[TransitCalculationResult]:
        """修改交通方式"""
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
            
        itinerary_service = self._create_itinerary_service()
        result = trip.modify_transit(
            day_index=day_index,
            transit_id=transit_id,
            operator_id=operator_id,
            itinerary_service=itinerary_service,
            transport_mode=transport_mode
        )
        
        if result:
            self._trip_repository.save(trip)
            self._publish_events(trip)
        
        return result

    def remove_activity(
        self,
        trip_id: str,
        day_index: int,
        activity_id: str,
        operator_id: str
    ) -> Optional[TransitCalculationResult]:
        """移除活动"""
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
        
        itinerary_service = self._create_itinerary_service()
        result = trip.remove_activity(day_index, activity_id, operator_id, itinerary_service)
        
        self._trip_repository.save(trip)
        self._publish_events(trip)
        
        return result or TransitCalculationResult()

    def update_day_itinerary(
        self,
        trip_id: str,
        day_index: int,
        activities_data: List[Dict[str, Any]],
        operator_id: str
    ) -> Optional[TransitCalculationResult]:
        """批量更新某日行程
        
        Args:
            trip_id: 旅行ID
            day_index: 日期索引
            activities_data: 活动数据列表
            operator_id: 操作者ID
        """
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
        
        # 构建活动列表
        activities = []
        for data in activities_data:
            loc_name = data['location_name']
            lat = data.get('latitude')
            lng = data.get('longitude')
            addr = data.get('address')

            # Auto-geocode if coordinates are missing
            if (lat is None or lng is None) and (loc_name or addr):
                try:
                    query = addr if addr else loc_name
                    geo_loc = self._geo_service.geocode(query)
                    if geo_loc:
                        lat = geo_loc.latitude
                        lng = geo_loc.longitude
                        if not addr:
                            addr = geo_loc.address
                except Exception as e:
                    print(f"Auto-geocode failed for {loc_name}: {e}")

            location = Location(
                name=loc_name,
                latitude=lat,
                longitude=lng,
                address=addr
            )
            cost_amount = data.get('cost_amount')
            cost = Money(Decimal(str(cost_amount)), data.get('cost_currency', 'CNY')) if cost_amount else None
            
            activity = Activity.create(
                name=data['name'],
                activity_type=ActivityType.from_string(data['activity_type']),
                location=location,
                start_time=data['start_time'],
                end_time=data['end_time'],
                cost=cost,
                notes=data.get('notes', '')
            )
            activities.append(activity)
        
        # 委托给聚合根
        itinerary_service = self._create_itinerary_service()
        result = trip.update_day_itinerary(day_index, activities, operator_id, itinerary_service)
        
        self._trip_repository.save(trip)
        self._publish_events(trip)
        
        return result or TransitCalculationResult()
    
    # ==================== 地理编码（无状态代理）====================
    
    def geocode_location(self, fuzzy_name: str) -> Optional[Dict[str, Any]]:
        """解析模糊地名为精确坐标
        
        直接委托给 IGeoService，无状态。
        
        Args:
            fuzzy_name: 模糊地名
            
        Returns:
            位置信息字典，包含 name, latitude, longitude, address
        """
        location = self._geo_service.geocode(fuzzy_name)
        if location:
            return {
                'name': location.name,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'address': location.address
            }
        return None
    
    # ==================== 统计报表 ====================
    
    def get_trip_statistics(self, trip_id: str) -> Optional[Dict[str, Any]]:
        """获取旅行统计报表
        
        委托给聚合根生成统计信息。
        
        Args:
            trip_id: 旅行ID
            
        Returns:
            统计信息字典
        """
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
        
        # 委托给聚合根
        stats = trip.generate_statistics()
        return stats.to_dict()
    
    # ==================== 状态管理 ====================
    
    def start_trip(self, trip_id: str) -> Optional[Trip]:
        """开始旅行"""
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
        
        trip.start()
        
        self._trip_repository.save(trip)
        self._publish_events(trip)
        
        return trip
    
    def complete_trip(self, trip_id: str) -> Optional[Trip]:
        """完成旅行"""
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
        
        trip.complete()
        
        self._trip_repository.save(trip)
        self._publish_events(trip)
        
        return trip
    
    def cancel_trip(self, trip_id: str, reason: Optional[str] = None) -> Optional[Trip]:
        """取消旅行"""
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
        
        trip.cancel(reason)
        
        self._trip_repository.save(trip)
        self._publish_events(trip)
        
        return trip
    
    # ==================== 日程备注 ====================
    
    def update_day_notes(self, trip_id: str, day_index: int, notes: str) -> Optional[Trip]:
        """更新日程备注"""
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
        
        trip.update_day_notes(day_index, notes)
        
        self._trip_repository.save(trip)
        self._publish_events(trip)
        
        return trip
    
    def update_day_theme(self, trip_id: str, day_index: int, theme: str) -> Optional[Trip]:
        """更新日程主题"""
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return None
        
        day = trip.get_day(day_index)
        if day:
            day.update_theme(theme)
            self._trip_repository.save(trip)
        
        return trip

    # ==================== 费用管理 ====================
    
    def add_expense(
        self,
        trip_id: str,
        description: str,
        amount: float,
        payer_id: str,
        category: str = "other",
        currency: str = "CNY",
        split_mode: str = "equal",
        participant_ids: Optional[List[str]] = None,
        exact_amounts: Optional[List[float]] = None,
        percentages: Optional[List[float]] = None,
        created_by: Optional[str] = None
    ) -> 'Expense':
        """添加费用
        
        Args:
            trip_id: 行程ID
            description: 费用描述
            amount: 总金额
            payer_id: 付款人ID
            category: 费用分类
            currency: 货币
            split_mode: 分摊方式 (equal/exact/percentage)
            participant_ids: 参与者ID列表（可选，默认为所有成员）
            exact_amounts: 精确金额列表（exact模式）
            percentages: 百分比列表（percentage模式）
            created_by: 创建者ID（可选，默认为付款人）
            
        Returns:
            创建的费用实体
            
        Raises:
            ValueError: 验证失败
        """
        from app_travel.domain.entity.expense import Expense
        from app_travel.domain.value_objects.expense_value_objects import (
            SplitMode, ExpenseCategory
        )
        from app_travel.domain.domain_event.expense_events import ExpenseAddedEvent
        from app_travel.infrastructure.database.dao_impl.sqlalchemy_expense_dao import SQLAlchemyExpenseDAO
        from app_travel.infrastructure.database.persistent_model.expense_po import ExpensePO
        from shared.database.core import get_db_session
        
        # 获取行程
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            raise ValueError(f"Trip {trip_id} not found")
        
        # 状态门控：只有 planning 或 in_progress 允许添加费用
        if trip.status not in [TripStatus.PLANNING, TripStatus.IN_PROGRESS]:
            raise ValueError(f"Cannot add expense to trip with status: {trip.status.value}")
        
        # 验证付款人是成员
        if not trip.is_member(payer_id):
            raise ValueError(f"Payer is not a member of this trip")
        
        # 默认参与者为所有成员
        if participant_ids is None:
            participant_ids = [m.user_id for m in trip.members]
        
        # 验证所有参与者都是成员
        for participant_id in participant_ids:
            if not trip.is_member(participant_id):
                raise ValueError(f"Participant {participant_id} is not a member of this trip")
        
        # 转换为 Decimal
        decimal_amount = Decimal(str(amount))
        decimal_exact_amounts = [Decimal(str(a)) for a in exact_amounts] if exact_amounts else None
        decimal_percentages = [Decimal(str(p)) for p in percentages] if percentages else None
        
        # 创建费用实体
        expense = Expense.create(
            trip_id=trip_id,
            description=description,
            amount=decimal_amount,
            payer_id=payer_id,
            participant_ids=participant_ids,
            split_mode=SplitMode.from_string(split_mode),
            category=ExpenseCategory.from_string(category),
            currency=currency,
            created_by=created_by,
            exact_amounts=decimal_exact_amounts,
            percentages=decimal_percentages
        )
        
        # 持久化
        session = get_db_session()
        expense_dao = SQLAlchemyExpenseDAO(session)
        expense_po = ExpensePO.from_domain(expense)
        expense_dao.create(expense_po)
        session.commit()
        
        # 发布事件
        event = ExpenseAddedEvent(
            trip_id=trip_id,
            expense_id=expense.id,
            payer_id=payer_id,
            amount=str(expense.amount),
            currency=currency,
            description=description
        )
        self._event_bus.publish(event)
        
        return expense
    
    def list_expenses(self, trip_id: str) -> List['Expense']:
        """获取行程的所有费用
        
        Args:
            trip_id: 行程ID
            
        Returns:
            费用列表
        """
        from app_travel.infrastructure.database.dao_impl.sqlalchemy_expense_dao import SQLAlchemyExpenseDAO
        from shared.database.core import get_db_session
        
        session = get_db_session()
        expense_dao = SQLAlchemyExpenseDAO(session)
        expense_pos = expense_dao.get_by_trip_id(trip_id)
        
        return [po.to_domain() for po in expense_pos]
    
    def delete_expense(
        self,
        trip_id: str,
        expense_id: str,
        deleted_by: str
    ) -> bool:
        """删除费用
        
        Args:
            trip_id: 行程ID
            expense_id: 费用ID
            deleted_by: 删除者ID
            
        Returns:
            是否成功删除
        """
        from app_travel.domain.domain_event.expense_events import ExpenseDeletedEvent
        from app_travel.infrastructure.database.dao_impl.sqlalchemy_expense_dao import SQLAlchemyExpenseDAO
        from shared.database.core import get_db_session
        
        # 验证行程存在
        trip = self._trip_repository.find_by_id(TripId(trip_id))
        if not trip:
            return False
        
        # 删除费用
        session = get_db_session()
        expense_dao = SQLAlchemyExpenseDAO(session)
        success = expense_dao.delete(expense_id)
        
        if success:
            session.commit()
            
            # 发布事件
            event = ExpenseDeletedEvent(
                trip_id=trip_id,
                expense_id=expense_id,
                deleted_by=deleted_by
            )
            self._event_bus.publish(event)
        
        return success
    
    def get_expense_summary(self, trip_id: str) -> Dict[str, Any]:
        """获取费用汇总
        
        Args:
            trip_id: 行程ID
            
        Returns:
            费用汇总信息
        """
        expenses = self.list_expenses(trip_id)
        
        if not expenses:
            return {
                'total_amount': 0,
                'currency': 'CNY',
                'per_member': {},
                'by_category': {}
            }
        
        # 总金额
        total_amount = sum(e.amount for e in expenses)
        currency = expenses[0].currency if expenses else 'CNY'
        
        # 每个成员的统计
        per_member = {}
        for expense in expenses:
            # 付款人
            if expense.payer_id not in per_member:
                per_member[expense.payer_id] = {'paid': Decimal('0'), 'owed': Decimal('0')}
            per_member[expense.payer_id]['paid'] += expense.amount
            
            # 参与者
            for share in expense.shares:
                if share.user_id not in per_member:
                    per_member[share.user_id] = {'paid': Decimal('0'), 'owed': Decimal('0')}
                per_member[share.user_id]['owed'] += share.amount
        
        # 转换为字符串
        per_member_str = {
            user_id: {
                'paid': str(stats['paid']),
                'owed': str(stats['owed'])
            }
            for user_id, stats in per_member.items()
        }
        
        # 按分类统计
        by_category = {}
        for expense in expenses:
            category = expense.category.value
            if category not in by_category:
                by_category[category] = Decimal('0')
            by_category[category] += expense.amount
        
        by_category_str = {cat: str(amt) for cat, amt in by_category.items()}
        
        return {
            'total_amount': str(total_amount),
            'currency': currency,
            'per_member': per_member_str,
            'by_category': by_category_str
        }
    
    def get_settlement(self, trip_id: str) -> List[Dict[str, Any]]:
        """获取结算方案
        
        Args:
            trip_id: 行程ID
            
        Returns:
            结算转账列表
        """
        from app_travel.domain.domain_service.settlement_service import SettlementService
        
        expenses = self.list_expenses(trip_id)
        
        if not expenses:
            return []
        
        # 计算余额
        balances = SettlementService.calculate_balances(expenses)
        
        # 最小化转账
        transfers = SettlementService.minimize_transfers(balances)
        
        # 转换为字典
        return [
            {
                'from_user_id': t.from_user_id,
                'to_user_id': t.to_user_id,
                'amount': str(t.amount),
                'currency': t.currency,
                'is_settled': t.is_settled
            }
            for t in transfers
        ]
    
    def mark_transfer_settled(
        self,
        trip_id: str,
        from_user_id: str,
        to_user_id: str,
        amount: float
    ) -> bool:
        """标记转账已结清
        
        Args:
            trip_id: 行程ID
            from_user_id: 付款方ID
            to_user_id: 收款方ID
            amount: 金额
            
        Returns:
            是否成功标记
        """
        from app_travel.domain.domain_event.expense_events import SettlementMarkedEvent
        from app_travel.infrastructure.database.dao_impl.sqlalchemy_expense_dao import SQLAlchemyExpenseDAO
        from app_travel.infrastructure.database.persistent_model.expense_po import SettlementTransferPO
        from shared.database.core import get_db_session
        
        # 查找或创建结算转账记录
        session = get_db_session()
        expense_dao = SQLAlchemyExpenseDAO(session)
        
        transfers = expense_dao.get_settlement_transfers_by_trip_id(trip_id)
        
        # 查找匹配的转账
        decimal_amount = Decimal(str(amount))
        target_transfer = None
        for transfer in transfers:
            if (transfer.from_user_id == from_user_id and
                transfer.to_user_id == to_user_id and
                transfer.amount == decimal_amount):
                target_transfer = transfer
                break
        
        if not target_transfer:
            # 创建新的转账记录
            from app_travel.domain.value_objects.expense_value_objects import SettlementTransfer
            transfer_vo = SettlementTransfer(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                amount=decimal_amount,
                currency='CNY',
                is_settled=True
            )
            transfer_po = SettlementTransferPO.from_domain(transfer_vo, trip_id)
            expense_dao.create_settlement_transfer(transfer_po)
        else:
            # 更新现有记录
            target_transfer.is_settled = True
            from datetime import datetime
            target_transfer.settled_at = datetime.utcnow()
            expense_dao.update_settlement_transfer(target_transfer)
        
        session.commit()
        
        # 发布事件
        event = SettlementMarkedEvent(
            trip_id=trip_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            amount=str(decimal_amount),
            currency='CNY'
        )
        self._event_bus.publish(event)
        
        return True

    # ==================== 模板管理 ====================
    
    def publish_template(
        self,
        trip_id: str,
        author_id: str
    ) -> Dict[str, Any]:
        """发布行程为模板
        
        Args:
            trip_id: 源行程ID
            author_id: 模板作者ID
            
        Returns:
            模板信息字典
            
        Raises:
            ValueError: 如果行程不满足发布条件
        """
        from app_travel.domain.domain_service.template_service import TemplateService
        from app_travel.infrastructure.database.repository_impl.template_repository_impl import TemplateRepositoryImpl
        from app_travel.infrastructure.database.dao_impl.sqlalchemy_template_dao import SQLAlchemyTemplateDAO
        from shared.database.core import get_db_session
        
        # 获取源行程
        trip = self.get_trip(trip_id)
        if not trip:
            raise ValueError(f"Trip {trip_id} not found")
        
        # 创建模板（会验证状态和可见性）
        template = TemplateService.create_from_trip(trip, author_id)
        
        # 持久化
        session = get_db_session()
        template_dao = SQLAlchemyTemplateDAO(session)
        template_repo = TemplateRepositoryImpl(template_dao)
        template_repo.save(template)
        session.commit()
        
        return {
            'id': template.id.value,
            'name': template.name,
            'description': template.description,
            'source_trip_id': template.source_trip_id,
            'author_id': template.author_id,
            'duration_days': template.duration_days,
            'tags': template.tags,
            'activity_count': template.activity_count,
            'created_at': template.created_at.isoformat()
        }
    
    def list_templates(
        self,
        limit: int = 20,
        offset: int = 0,
        keyword: Optional[str] = None,
        tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """浏览模板列表
        
        Args:
            limit: 每页数量
            offset: 偏移量
            keyword: 关键词搜索（可选）
            tag: 标签过滤（可选）
            
        Returns:
            包含模板列表和总数的字典
        """
        from app_travel.infrastructure.database.repository_impl.template_repository_impl import TemplateRepositoryImpl
        from app_travel.infrastructure.database.dao_impl.sqlalchemy_template_dao import SQLAlchemyTemplateDAO
        from shared.database.core import get_db_session
        
        session = get_db_session()
        template_dao = SQLAlchemyTemplateDAO(session)
        template_repo = TemplateRepositoryImpl(template_dao)
        
        templates = template_repo.find_all(
            limit=limit,
            offset=offset,
            keyword=keyword,
            tag=tag
        )
        
        total = template_repo.count_all(keyword=keyword, tag=tag)
        
        template_list = [
            {
                'id': t.id.value,
                'name': t.name,
                'description': t.description,
                'author_id': t.author_id,
                'duration_days': t.duration_days,
                'tags': t.tags,
                'activity_count': t.activity_count,
                'created_at': t.created_at.isoformat()
            }
            for t in templates
        ]
        
        return {
            'templates': template_list,
            'total': total,
            'limit': limit,
            'offset': offset
        }
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """获取模板详情
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板详情字典，不存在返回 None
        """
        from app_travel.domain.value_objects.template_value_objects import TemplateId
        from app_travel.infrastructure.database.repository_impl.template_repository_impl import TemplateRepositoryImpl
        from app_travel.infrastructure.database.dao_impl.sqlalchemy_template_dao import SQLAlchemyTemplateDAO
        from shared.database.core import get_db_session
        
        session = get_db_session()
        template_dao = SQLAlchemyTemplateDAO(session)
        template_repo = TemplateRepositoryImpl(template_dao)
        
        template = template_repo.find_by_id(TemplateId(template_id))
        
        if not template:
            return None
        
        # 转换日程数据
        days_data = []
        for day_data in template.days_data:
            activities = [
                {
                    'name': a.name,
                    'activity_type': a.activity_type,
                    'location_name': a.location_name,
                    'latitude': a.latitude,
                    'longitude': a.longitude,
                    'address': a.address,
                    'duration_minutes': a.duration_minutes,
                    'cost_amount': a.cost_amount,
                    'cost_currency': a.cost_currency,
                    'notes': a.notes
                }
                for a in day_data.activities
            ]
            
            days_data.append({
                'day_number': day_data.day_number,
                'theme': day_data.theme,
                'activities': activities
            })
        
        return {
            'id': template.id.value,
            'name': template.name,
            'description': template.description,
            'source_trip_id': template.source_trip_id,
            'author_id': template.author_id,
            'duration_days': template.duration_days,
            'tags': template.tags,
            'activity_count': template.activity_count,
            'days_data': days_data,
            'created_at': template.created_at.isoformat()
        }
    
    def clone_from_template(
        self,
        template_id: str,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> Trip:
        """从模板克隆行程
        
        Args:
            template_id: 模板ID
            user_id: 新行程创建者ID
            start_date: 新行程开始日期
            end_date: 新行程结束日期
            
        Returns:
            新创建的行程
            
        Raises:
            ValueError: 如果模板不存在或日期无效
        """
        from app_travel.domain.value_objects.template_value_objects import TemplateId
        from app_travel.domain.domain_service.template_service import TemplateService
        from app_travel.infrastructure.database.repository_impl.template_repository_impl import TemplateRepositoryImpl
        from app_travel.infrastructure.database.dao_impl.sqlalchemy_template_dao import SQLAlchemyTemplateDAO
        from shared.database.core import get_db_session
        
        # 获取模板
        session = get_db_session()
        template_dao = SQLAlchemyTemplateDAO(session)
        template_repo = TemplateRepositoryImpl(template_dao)
        
        template = template_repo.find_by_id(TemplateId(template_id))
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # 克隆为新行程
        trip = TemplateService.clone_to_trip(template, user_id, start_date, end_date)
        
        # 持久化
        self._trip_repository.save(trip)
        
        # 发布事件
        self._publish_events(trip)
        
        return trip
    
    def clone_from_trip(
        self,
        source_trip_id: str,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> Trip:
        """直接克隆公开行程
        
        Args:
            source_trip_id: 源行程ID
            user_id: 新行程创建者ID
            start_date: 新行程开始日期
            end_date: 新行程结束日期
            
        Returns:
            新创建的行程
            
        Raises:
            ValueError: 如果源行程不存在、不公开或日期无效
        """
        from app_travel.domain.domain_service.template_service import TemplateService
        
        # 获取源行程
        source_trip = self.get_trip(source_trip_id)
        if not source_trip:
            raise ValueError(f"Trip {source_trip_id} not found")
        
        # 克隆行程
        trip = TemplateService.clone_trip_directly(source_trip, user_id, start_date, end_date)
        
        # 持久化
        self._trip_repository.save(trip)
        
        # 发布事件
        self._publish_events(trip)
        
        return trip
