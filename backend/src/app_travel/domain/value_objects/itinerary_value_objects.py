"""
行程相关值对象定义

包含行程警告、交通计算结果等值对象。
"""
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app_travel.domain.entity.transit import Transit


@dataclass(frozen=True)
class ItineraryWarning:
    """行程警告值对象
    
    当行程存在问题时生成警告，例如：
    - 活动A结束时间10:00，活动B开始时间10:10，但路程需要30分钟
    """
    warning_type: str  # "time_conflict", "unreachable", "overlap", etc.
    message: str
    from_activity_id: str
    to_activity_id: str
    required_time_minutes: int   # 所需时间（分钟）
    available_time_minutes: int  # 可用时间（分钟）
    
    @classmethod
    def time_conflict(
        cls,
        from_activity_id: str,
        to_activity_id: str,
        required_minutes: int,
        available_minutes: int
    ) -> 'ItineraryWarning':
        """创建时间冲突警告"""
        return cls(
            warning_type="time_conflict",
            message=f"行程时间不足：需要{required_minutes}分钟，但只有{available_minutes}分钟",
            from_activity_id=from_activity_id,
            to_activity_id=to_activity_id,
            required_time_minutes=required_minutes,
            available_time_minutes=available_minutes
        )
    
    @classmethod
    def unreachable(
        cls,
        from_activity_id: str,
        to_activity_id: str,
        message: str = "无法到达目的地"
    ) -> 'ItineraryWarning':
        """创建无法到达警告"""
        return cls(
            warning_type="unreachable",
            message=message,
            from_activity_id=from_activity_id,
            to_activity_id=to_activity_id,
            required_time_minutes=0,
            available_time_minutes=0
        )


@dataclass
class TransitCalculationResult:
    """交通计算结果值对象
    
    包含计算出的交通列表和可能的警告。
    """
    transits: List['Transit'] = field(default_factory=list)
    warnings: List[ItineraryWarning] = field(default_factory=list)
    
    @property
    def has_warnings(self) -> bool:
        """是否存在警告"""
        return len(self.warnings) > 0
    
    @property
    def is_feasible(self) -> bool:
        """行程是否可行（无时间冲突警告）"""
        return not any(w.warning_type == "time_conflict" for w in self.warnings)
    
    def add_transit(self, transit: 'Transit') -> None:
        """添加交通"""
        self.transits.append(transit)
    
    def add_warning(self, warning: ItineraryWarning) -> None:
        """添加警告"""
        self.warnings.append(warning)
