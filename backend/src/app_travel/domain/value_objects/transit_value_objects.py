"""
Transit 相关值对象定义

包含交通方式、路线信息、交通费用等值对象。
"""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional

from app_travel.domain.value_objects.travel_value_objects import Money


class TransportMode(Enum):
    """交通方式枚举"""
    DRIVING = "driving"      # 驾车
    WALKING = "walking"      # 步行
    TRANSIT = "transit"      # 公交
    CYCLING = "cycling"      # 骑行
    
    @classmethod
    def from_string(cls, mode_str: str) -> 'TransportMode':
        """从字符串创建交通方式"""
        mode_str = mode_str.lower()
        for mode in cls:
            if mode.value == mode_str:
                return mode
        raise ValueError(f"Unknown transport mode: {mode_str}")


@dataclass(frozen=True)
class RouteInfo:
    """路线信息值对象
    
    包含距离、耗时和可选的路线编码。
    """
    distance_meters: float    # 距离（米）
    duration_seconds: int     # 耗时（秒）
    polyline: Optional[str] = None  # 路线编码（可选，用于地图绘制）
    
    def __post_init__(self):
        if self.distance_meters < 0:
            raise ValueError("Distance cannot be negative")
        if self.duration_seconds < 0:
            raise ValueError("Duration cannot be negative")
    
    @property
    def distance_km(self) -> float:
        """获取距离（公里）"""
        return self.distance_meters / 1000
    
    @property
    def duration_minutes(self) -> int:
        """获取耗时（分钟）"""
        return self.duration_seconds // 60
    
    @classmethod
    def zero(cls) -> 'RouteInfo':
        """创建零路线信息"""
        return cls(distance_meters=0.0, duration_seconds=0)


@dataclass(frozen=True)
class TransitCost:
    """交通费用值对象
    
    包含预估总费用和细分费用。
    费用计算规则：
    - 驾车：CNY 0.5/km 油费 + CNY 5 基础费用
    - 公交：CNY 3 每次
    - 步行/骑行：免费
    """
    estimated_cost: Money     # 预估总费用
    fuel_cost: Optional[Money] = None    # 油费（驾车）
    toll_cost: Optional[Money] = None    # 过路费（驾车）
    ticket_cost: Optional[Money] = None  # 车票费用（公交/地铁）
    
    @classmethod
    def calculate_for_mode(
        cls,
        mode: TransportMode,
        distance_meters: float,
        toll_cost: Optional[Money] = None
    ) -> 'TransitCost':
        """根据交通方式和距离计算费用
        
        Args:
            mode: 交通方式
            distance_meters: 距离（米）
            toll_cost: 过路费（可选，仅驾车有效）
            
        Returns:
            TransitCost: 计算后的交通费用
        """
        distance_km = distance_meters / 1000
        
        if mode == TransportMode.DRIVING:
            # 驾车：CNY 0.5/km 油费 + CNY 5 基础费用
            fuel = Money(Decimal(str(distance_km * 0.5)), "CNY")
            base_fee = Money(Decimal("5"), "CNY")
            total = fuel + base_fee
            if toll_cost:
                total = total + toll_cost
            return cls(
                estimated_cost=total,
                fuel_cost=fuel,
                toll_cost=toll_cost
            )
        elif mode == TransportMode.TRANSIT:
            # 公交：CNY 3 每次
            ticket = Money(Decimal("3"), "CNY")
            return cls(
                estimated_cost=ticket,
                ticket_cost=ticket
            )
        else:
            # 步行/骑行：免费
            return cls(estimated_cost=Money.zero())
    
    @classmethod
    def zero(cls) -> 'TransitCost':
        """创建零费用"""
        return cls(estimated_cost=Money.zero())
