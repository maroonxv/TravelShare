"""
旅行仓库接口
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app_travel.domain.aggregate.trip_aggregate import Trip
from app_travel.domain.value_objects.travel_value_objects import TripId, TripStatus


class ITripRepository(ABC):
    """旅行仓库接口"""
    
    @abstractmethod
    def save(self, trip: Trip) -> None:
        """保存旅行（新增或更新）
        
        Args:
            trip: 旅行聚合根
        """
        pass
    
    @abstractmethod
    def find_by_id(self, trip_id: TripId) -> Optional[Trip]:
        """根据ID查找旅行
        
        Args:
            trip_id: 旅行ID
            
        Returns:
            旅行实例，不存在则返回 None
        """
        pass
    
    @abstractmethod
    def find_by_member(self, user_id: str, status: Optional[TripStatus] = None) -> List[Trip]:
        """查找用户参与的旅行
        
        Args:
            user_id: 用户ID
            status: 可选的状态筛选
            
        Returns:
            旅行列表
        """
        pass
    
    @abstractmethod
    def find_by_creator(self, creator_id: str) -> List[Trip]:
        """查找用户创建的旅行
        
        Args:
            creator_id: 创建者ID
            
        Returns:
            旅行列表
        """
        pass
    
    @abstractmethod
    def find_public(self, limit: int = 20, offset: int = 0) -> List[Trip]:
        """查找公开的旅行
        
        Args:
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            旅行列表
        """
        pass
    
    @abstractmethod
    def delete(self, trip_id: TripId) -> None:
        """删除旅行
        
        Args:
            trip_id: 旅行ID
        """
        pass
    
    @abstractmethod
    def exists(self, trip_id: TripId) -> bool:
        """检查旅行是否存在
        
        Args:
            trip_id: 旅行ID
            
        Returns:
            是否存在
        """
        pass