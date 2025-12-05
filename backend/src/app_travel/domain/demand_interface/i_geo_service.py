"""
地理服务接口

调用外部地图API的抽象接口。
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from app_travel.domain.value_objects.travel_value_objects import Location


class IGeoService(ABC):
    """地理服务接口"""
    
    @abstractmethod
    def geocode(self, address: str) -> Optional[Location]:
        """地址转坐标（地理编码）
        
        Args:
            address: 地址字符串
            
        Returns:
            位置信息，如果无法解析返回 None
        """
        pass
    
    @abstractmethod
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """坐标转地址（逆地理编码）
        
        Args:
            latitude: 纬度
            longitude: 经度
            
        Returns:
            地址字符串，如果无法解析返回 None
        """
        pass
    
    @abstractmethod
    def calculate_distance(self, origin: Location, destination: Location) -> float:
        """计算两点之间的距离
        
        Args:
            origin: 起点
            destination: 终点
            
        Returns:
            距离（米）
        """
        pass
    
    @abstractmethod
    def get_route(
        self,
        origin: Location,
        destination: Location,
        mode: str = "driving"
    ) -> Dict[str, Any]:
        """获取路线信息
        
        Args:
            origin: 起点
            destination: 终点
            mode: 出行方式 (driving, walking, transit, cycling)
            
        Returns:
            路线信息字典，包含距离、时间、路线点等
        """
        pass
    
    @abstractmethod
    def search_places(
        self,
        keyword: str,
        location: Optional[Location] = None,
        radius: int = 5000
    ) -> List[Location]:
        """搜索地点
        
        Args:
            keyword: 搜索关键词
            location: 中心位置（可选）
            radius: 搜索半径（米）
            
        Returns:
            位置列表
        """
        pass