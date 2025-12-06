"""
ItineraryItem 实体 - 行程项

表示行程中的一个有序项目，可以是 Activity 或 Transit。
用于维护 Activity 和 Transit 之间的先后顺序。
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from app_travel.domain.entity.activity import Activity
    from app_travel.domain.entity.transit import Transit


class ItineraryItemType(Enum):
    """行程项类型枚举"""
    ACTIVITY = "activity"
    TRANSIT = "transit"


@dataclass
class ItineraryItem:
    """行程项实体
    
    表示行程中的一个有序项目，用于维护 Activity 和 Transit 的先后顺序。
    行程的顺序为：Activity_1 -> Transit_1_2 -> Activity_2 -> Transit_2_3 -> Activity_3 -> ...
    """
    
    sequence: int           # 序号（用于排序，从0开始）
    item_type: ItineraryItemType
    activity: Optional['Activity'] = None
    transit: Optional['Transit'] = None
    
    def __post_init__(self):
        """验证行程项的有效性"""
        if self.item_type == ItineraryItemType.ACTIVITY:
            if self.activity is None:
                raise ValueError("Activity item must have an activity")
            if self.transit is not None:
                raise ValueError("Activity item cannot have a transit")
        elif self.item_type == ItineraryItemType.TRANSIT:
            if self.transit is None:
                raise ValueError("Transit item must have a transit")
            if self.activity is not None:
                raise ValueError("Transit item cannot have an activity")
    
    @classmethod
    def from_activity(cls, sequence: int, activity: 'Activity') -> 'ItineraryItem':
        """从 Activity 创建行程项
        
        Args:
            sequence: 序号
            activity: 活动实体
            
        Returns:
            ItineraryItem: 活动类型的行程项
        """
        return cls(
            sequence=sequence,
            item_type=ItineraryItemType.ACTIVITY,
            activity=activity
        )
    
    @classmethod
    def from_transit(cls, sequence: int, transit: 'Transit') -> 'ItineraryItem':
        """从 Transit 创建行程项
        
        Args:
            sequence: 序号
            transit: 交通实体
            
        Returns:
            ItineraryItem: 交通类型的行程项
        """
        return cls(
            sequence=sequence,
            item_type=ItineraryItemType.TRANSIT,
            transit=transit
        )
    
    @property
    def is_activity(self) -> bool:
        """是否为活动类型"""
        return self.item_type == ItineraryItemType.ACTIVITY
    
    @property
    def is_transit(self) -> bool:
        """是否为交通类型"""
        return self.item_type == ItineraryItemType.TRANSIT
    
    @property
    def item_id(self) -> str:
        """获取项目ID（Activity或Transit的ID）"""
        if self.is_activity:
            return self.activity.id
        else:
            return self.transit.id
    
    def get_item(self) -> Union['Activity', 'Transit']:
        """获取实际的Activity或Transit对象"""
        if self.is_activity:
            return self.activity
        else:
            return self.transit
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ItineraryItem):
            return False
        return self.sequence == other.sequence and self.item_type == other.item_type
    
    def __hash__(self) -> int:
        return hash((self.sequence, self.item_type))
    
    def __lt__(self, other: 'ItineraryItem') -> bool:
        """用于排序"""
        return self.sequence < other.sequence
    
    def __repr__(self) -> str:
        if self.is_activity:
            return f"ItineraryItem(seq={self.sequence}, type=ACTIVITY, id={self.activity.id})"
        else:
            return f"ItineraryItem(seq={self.sequence}, type=TRANSIT, id={self.transit.id})"
