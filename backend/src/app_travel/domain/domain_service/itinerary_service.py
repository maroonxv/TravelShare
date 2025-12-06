"""
ItineraryService 领域服务 - 智能行程管家

负责计算活动之间的交通路线、验证行程可行性、地址解析等。
"""
from datetime import datetime, date
from typing import List, Optional

from app_travel.domain.entity.activity import Activity
from app_travel.domain.entity.transit import Transit
from app_travel.domain.value_objects.transit_value_objects import (
    TransportMode, RouteInfo, TransitCost
)
from app_travel.domain.value_objects.itinerary_value_objects import (
    ItineraryWarning, TransitCalculationResult
)
from app_travel.domain.value_objects.travel_value_objects import Location
from app_travel.domain.demand_interface.i_geo_service import IGeoService


class ItineraryService:
    """智能行程管家 - 领域服务
    
    职责：
    1. 计算活动之间的最佳交通路线
    2. 解析模糊地名获取精确坐标
    3. 验证行程可行性（检测时间冲突）
    
    规则：
    - 默认使用驾车模式计算路线
    - 如果两个活动之间距离 < 2km，默认使用步行模式
    """
    
    # 步行距离阈值（米）
    WALKING_DISTANCE_THRESHOLD = 2000
    
    def __init__(self, geo_service: IGeoService):
        """初始化行程服务
        
        Args:
            geo_service: 地理服务接口
        """
        self._geo_service = geo_service
    
    def calculate_transits_between_activities(
        self,
        activities: List[Activity],
        mode: TransportMode = TransportMode.DRIVING
    ) -> TransitCalculationResult:
        """计算活动列表中两两之间的最佳路径
        
        按时间顺序计算相邻活动之间的交通。
        如果距离 < 2km，自动切换为步行模式。
        
        Args:
            activities: 活动列表（会按开始时间排序）
            mode: 默认交通方式，默认驾车
            
        Returns:
            TransitCalculationResult: 包含Transit列表和警告
        """
        result = TransitCalculationResult()
        
        if len(activities) < 2:
            return result
        
        # 按开始时间排序
        sorted_activities = sorted(activities, key=lambda a: a.start_time)
        
        # 计算相邻活动之间的交通
        for i in range(len(sorted_activities) - 1):
            from_activity = sorted_activities[i]
            to_activity = sorted_activities[i + 1]
            
            try:
                transit = self.calculate_transit_between_two_activities(
                    from_activity, to_activity, mode
                )
                result.add_transit(transit)
                
                # 检查时间是否足够
                warning = self._check_time_feasibility(
                    from_activity, to_activity, transit
                )
                if warning:
                    result.add_warning(warning)
                    
            except Exception as e:
                # 无法计算路线时添加警告
                result.add_warning(ItineraryWarning.unreachable(
                    from_activity.id,
                    to_activity.id,
                    f"无法计算路线: {str(e)}"
                ))
        
        return result
    
    def calculate_transit_between_two_activities(
        self,
        from_activity: Activity,
        to_activity: Activity,
        mode: TransportMode = TransportMode.DRIVING
    ) -> Transit:
        """计算两个活动之间的交通
        
        如果距离 < 2km，自动切换为步行模式。
        
        Args:
            from_activity: 起始活动
            to_activity: 目标活动
            mode: 默认交通方式
            
        Returns:
            Transit: 交通实体
        """
        origin = from_activity.location
        destination = to_activity.location
        
        # 先计算直线距离判断是否使用步行
        actual_mode = mode
        straight_distance = self._geo_service.calculate_distance(origin, destination)
        
        if straight_distance < self.WALKING_DISTANCE_THRESHOLD:
            actual_mode = TransportMode.WALKING
        
        # 获取路线信息
        route_data = self._geo_service.get_route(
            origin, destination, actual_mode.value
        )
        
        # 解析路线信息
        route_info = self._parse_route_info(route_data)
        
        # 创建 Transit
        transit = Transit.create_from_activities(
            from_activity, to_activity, route_info, actual_mode
        )
        
        return transit
    
    def geocode_fuzzy_location(self, fuzzy_name: str) -> Location:
        """根据模糊地名获取精确坐标和标准地址
        
        Args:
            fuzzy_name: 模糊地名（如"故宫"、"颐和园"）
            
        Returns:
            Location: 包含精确坐标和标准地址的位置对象
            
        Raises:
            ValueError: 如果无法解析地址
        """
        location = self._geo_service.geocode(fuzzy_name)
        if location is None:
            raise ValueError(f"无法解析地址: {fuzzy_name}")
        return location
    
    def validate_itinerary_feasibility(
        self,
        activities: List[Activity],
        transits: List[Transit]
    ) -> List[ItineraryWarning]:
        """验证行程是否可行
        
        检查每个活动结束时间 + 交通时间 是否 <= 下一活动开始时间
        
        Args:
            activities: 活动列表
            transits: 交通列表
            
        Returns:
            List[ItineraryWarning]: 警告列表（空列表表示可行）
        """
        warnings: List[ItineraryWarning] = []
        
        if len(activities) < 2:
            return warnings
        
        # 按开始时间排序
        sorted_activities = sorted(activities, key=lambda a: a.start_time)
        
        # 建立Transit查找字典
        transit_map = {
            (t.from_activity_id, t.to_activity_id): t 
            for t in transits
        }
        
        # 检查每对相邻活动
        for i in range(len(sorted_activities) - 1):
            from_activity = sorted_activities[i]
            to_activity = sorted_activities[i + 1]
            
            transit = transit_map.get((from_activity.id, to_activity.id))
            if transit:
                warning = self._check_time_feasibility(
                    from_activity, to_activity, transit
                )
                if warning:
                    warnings.append(warning)
        
        return warnings
    
    def _check_time_feasibility(
        self,
        from_activity: Activity,
        to_activity: Activity,
        transit: Transit
    ) -> Optional[ItineraryWarning]:
        """检查两个活动之间的时间是否足够
        
        Args:
            from_activity: 起始活动
            to_activity: 目标活动
            transit: 交通信息
            
        Returns:
            ItineraryWarning 或 None（时间足够时）
        """
        # 计算可用时间（从活动A结束到活动B开始）
        from_end = datetime.combine(date.today(), from_activity.end_time)
        to_start = datetime.combine(date.today(), to_activity.start_time)
        available_minutes = int((to_start - from_end).total_seconds() / 60)
        
        # 所需时间
        required_minutes = transit.duration_minutes
        
        if required_minutes > available_minutes:
            return ItineraryWarning.time_conflict(
                from_activity.id,
                to_activity.id,
                required_minutes,
                available_minutes
            )
        
        return None
    
    def _parse_route_info(self, route_data: dict) -> RouteInfo:
        """解析路线数据为 RouteInfo
        
        Args:
            route_data: 从 IGeoService.get_route() 返回的数据
            
        Returns:
            RouteInfo: 路线信息值对象
        """
        if not route_data or 'paths' not in route_data or not route_data['paths']:
            # 如果无法获取路线，返回零路线
            return RouteInfo.zero()
        
        # 取第一条路线
        path = route_data['paths'][0]
        
        return RouteInfo(
            distance_meters=float(path.get('distance', 0)),
            duration_seconds=int(path.get('duration', 0)),
            polyline=path.get('polyline')
        )
