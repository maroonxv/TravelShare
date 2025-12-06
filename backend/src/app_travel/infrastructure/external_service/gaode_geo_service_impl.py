import requests
from typing import Optional, List, Dict, Any
from app_travel.domain.demand_interface.i_geo_service import IGeoService
from app_travel.domain.value_objects.travel_value_objects import Location

class GaodeGeoServiceImpl(IGeoService):
    """基于高德地图 Web 服务 API 的地理服务实现"""

    def __init__(self, api_key: str = "615fc65de7dcae0a3b68b67ca8746591"):
        self.api_key = api_key
        self.base_url = "https://restapi.amap.com/v3"

    def geocode(self, address: str) -> Optional[Location]:
        """地址转坐标（地理编码）"""
        url = f"{self.base_url}/geocode/geo"
        params = {
            "key": self.api_key,
            "address": address,
            "output": "json"
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("status") == "1" and data.get("geocodes"):
                geocode = data["geocodes"][0]
                location_str = geocode.get("location", "")
                if location_str:
                    lng, lat = map(float, location_str.split(","))
                    return Location(
                        name=address,
                        latitude=lat,
                        longitude=lng,
                        address=geocode.get("formatted_address", address)
                    )
            return None
        except Exception as e:
            print(f"Geocode error: {e}")
            return None

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """坐标转地址（逆地理编码）"""
        url = f"{self.base_url}/geocode/regeo"
        params = {
            "key": self.api_key,
            "location": f"{longitude},{latitude}",
            "output": "json"
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("status") == "1" and data.get("regeocode"):
                return data["regeocode"].get("formatted_address")
            return None
        except Exception as e:
            print(f"Reverse geocode error: {e}")
            return None

    def calculate_distance(self, origin: Location, destination: Location) -> float:
        """计算两点之间的距离"""
        if not origin.has_coordinates() or not destination.has_coordinates():
            # 如果没有坐标，先尝试地理编码
            if not origin.has_coordinates():
                origin_loc = self.geocode(origin.name)
                if not origin_loc: return 0.0
                origin = origin_loc
            if not destination.has_coordinates():
                dest_loc = self.geocode(destination.name)
                if not dest_loc: return 0.0
                destination = dest_loc
        
        url = f"{self.base_url}/distance"
        params = {
            "key": self.api_key,
            "origins": f"{origin.longitude},{origin.latitude}",
            "destination": f"{destination.longitude},{destination.latitude}",
            "type": "1", # 1: 直线距离
            "output": "json"
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("status") == "1" and data.get("results"):
                return float(data["results"][0]["distance"])
            return 0.0
        except Exception as e:
            print(f"Calculate distance error: {e}")
            return 0.0

    def get_route(
        self,
        origin: Location,
        destination: Location,
        mode: str = "driving"
    ) -> Dict[str, Any]:
        """获取路线信息
        mode: driving (驾车), walking (步行), transit (公交), bicycling (骑行)
        """
        # 确保有坐标
        if not origin.has_coordinates():
            loc = self.geocode(origin.name)
            if loc: origin = loc
        if not destination.has_coordinates():
            loc = self.geocode(destination.name)
            if loc: destination = loc
            
        if not origin.has_coordinates() or not destination.has_coordinates():
            return {}

        # 映射 mode 到高德 API 路径
        mode_map = {
            "driving": "direction/driving",
            "walking": "direction/walking",
            "transit": "direction/transit/integrated",
            "cycling": "direction/bicycling",
            "bicycling": "direction/bicycling"
        }
        
        api_path = mode_map.get(mode, "direction/driving")
        url = f"{self.base_url}/{api_path}"
        
        params = {
            "key": self.api_key,
            "origin": f"{origin.longitude},{origin.latitude}",
            "destination": f"{destination.longitude},{destination.latitude}",
            "output": "json"
        }
        
        if mode == "transit":
            # 公交路径规划需要城市信息，这里简单处理，假设同城或必填
            # 实际应用中可能需要先通过逆地理编码获取城市代码
            params["city"] = "北京" # 示例默认值，实际应动态获取
            
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("status") == "1" and data.get("route"):
                route = data["route"]
                result = {
                    "origin": f"{origin.longitude},{origin.latitude}",
                    "destination": f"{destination.longitude},{destination.latitude}",
                    "paths": []
                }
                
                paths = route.get("paths", [])
                if mode == "transit":
                    paths = route.get("transits", [])
                    
                for p in paths:
                    path_info = {
                        "distance": float(p.get("distance", 0)),
                        "duration": float(p.get("duration", 0)),
                        "steps": []
                    }
                    # 简化步骤信息
                    steps = p.get("steps", [])
                    if mode == "transit":
                        steps = p.get("segments", []) # 公交是 segments
                        
                    path_info["steps"] = len(steps)
                    result["paths"].append(path_info)
                    
                return result
            return {}
        except Exception as e:
            print(f"Get route error: {e}")
            return {}

    def search_places(
        self,
        keyword: str,
        location: Optional[Location] = None,
        radius: int = 5000
    ) -> List[Location]:
        """搜索地点 (POI 搜索)"""
        url = f"{self.base_url}/place/text"
        params = {
            "key": self.api_key,
            "keywords": keyword,
            "output": "json",
            "offset": 20,
            "page": 1
        }
        
        if location and location.has_coordinates():
            # 周边搜索
            url = f"{self.base_url}/place/around"
            params["location"] = f"{location.longitude},{location.latitude}"
            params["radius"] = radius
            del params["keywords"] # 周边搜索用 keywords 也可以，但这里保持逻辑清晰
            params["keywords"] = keyword # 其实周边搜索也需要关键词

        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            results = []
            if data.get("status") == "1" and data.get("pois"):
                for poi in data["pois"]:
                    location_str = poi.get("location", "")
                    if location_str:
                        lng, lat = map(float, location_str.split(","))
                        results.append(Location(
                            name=poi.get("name"),
                            latitude=lat,
                            longitude=lng,
                            address=poi.get("address") or poi.get("pname") + poi.get("cityname") + poi.get("adname")
                        ))
            return results
        except Exception as e:
            print(f"Search places error: {e}")
            return []
