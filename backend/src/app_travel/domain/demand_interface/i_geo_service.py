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
            address: 结构化地址字符串 (如 "北京市朝阳区阜通东大街6号")
            
        Returns:
            Location: 包含坐标的位置对象。
                      - 如果解析成功，返回的 Location 对象将包含 name(原地址), latitude, longitude, address(标准地址)。
                      - 如果解析失败或无结果，返回 None。
        """
        pass
    
    @abstractmethod
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """坐标转地址（逆地理编码）
        
        Args:
            latitude: 纬度 (范围 -90 到 90)
            longitude: 经度 (范围 -180 到 180)
            
        Returns:
            str: 解析后的结构化地址字符串 (如 "北京市朝阳区望京街道...")。
                 如果解析失败，返回 None。
        """
        pass
    
    @abstractmethod
    def calculate_distance(self, origin: Location, destination: Location) -> float:
        """计算两点之间的直线距离
        
        Args:
            origin: 起点 Location 对象。
                    如果对象中缺少坐标，会自动调用 geocode 尝试获取。
            destination: 终点 Location 对象。
                         如果对象中缺少坐标，会自动调用 geocode 尝试获取。
            
        Returns:
            float: 两点间的直线距离，单位：米。
                   如果无法计算（如坐标缺失且无法解析），返回 0.0。
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
            origin: 起点 (需要包含坐标或地址)
            destination: 终点 (需要包含坐标或地址)
            mode: 出行方式，可选值：
                  - "driving": 驾车 (默认)
                  - "walking": 步行
                  - "transit": 公交
                  - "cycling" / "bicycling": 骑行
            
        Returns:
            路线信息字典，结构示例:
            {
                "origin": "116.481028,39.989643",      # 起点坐标
                "destination": "116.434446,39.90816", # 终点坐标
                "paths": [                            # 可选路线列表
                    {
                        "distance": 1000.0,           # 距离 (米)
                        "duration": 600.0,            # 预计耗时 (秒)
                        "steps": 15                   # 导航段数
                    }
                ]
            }
            如果获取失败或无路线，返回空字典 {}。
        """
        pass
    
    @abstractmethod
    def search_places(
        self,
        keyword: str,
        location: Optional[Location] = None,
        radius: int = 5000
    ) -> List[Location]:
        """搜索地点 (POI搜索)
        
        Args:
            keyword: 搜索关键词 (如 "咖啡", "清华大学")
            location: 中心位置 (可选)。如果不传，则进行全局关键字搜索；如果传入且包含坐标，则进行周边搜索。
            radius: 搜索半径 (米)，仅在周边搜索 (location不为空) 时有效。默认 5000米。
            
        Returns:
            位置对象列表 (List[Location])。
            每个 Location 对象包含:
            - name: 地点名称
            - latitude/longitude: 坐标
            - address: 详细地址
            如果无结果或出错，返回空列表 []。
        """
        pass