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

    def _get_city_info(self, latitude: float, longitude: float) -> str:
        """获取坐标所在的城市信息（用于公交规划）
        优先返回 adcode，其次 city 名称，再次 province 名称
        """
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
                comp = data["regeocode"].get("addressComponent", {})
                
                # 优先使用 citycode (API要求 city1 参数为 citycode)
                citycode = comp.get("citycode")
                if citycode and isinstance(citycode, str):
                    return citycode
                elif citycode and isinstance(citycode, list) and len(citycode) > 0:
                     return str(citycode[0])
                
                # 如果没有 citycode，尝试使用 adcode (虽然文档说只支持 citycode，但在某些情况下 adcode 可能有用，或者作为备选)
                # 但根据文档严格性，如果没有 citycode，可能无法进行公交规划
                # 这里我们尽量返回一个有意义的值，或者默认 010
                if comp.get("adcode"):
                    # 注意：有些文档暗示 citycode 字段为空时可能是直辖市，此时 adcode 前4位或3位可能对应 citycode？
                    # 但通常直辖市也有 citycode (010, 021 etc)
                    pass

            return "010" # 默认降级为北京 citycode
        except Exception as e:
            print(f"Get city info error: {e}")
            return "010"

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

        # 映射 mode 到高德 API 路径 (API 2.0 / v5)
        # 文档参考: GAODE_API_DOC.md
        mode_map = {
            "driving": "direction/driving",
            "walking": "direction/walking",
            "transit": "direction/transit/integrated",
            "cycling": "direction/bicycling",
            "bicycling": "direction/bicycling"
        }
        
        # 默认使用 v5 接口
        api_path = mode_map.get(mode, "direction/driving")
        # 注意：v5 接口的 base_url 通常是 https://restapi.amap.com/v5
        # 原有的 self.base_url 是 v3，我们需要区分处理或者统一升级
        # 这里为了稳妥，针对路径规划使用 v5
        base_url_v5 = "https://restapi.amap.com/v5"
        url = f"{base_url_v5}/{api_path}"
        
        params = {
            "key": self.api_key,
            "origin": f"{origin.longitude},{origin.latitude}",
            "destination": f"{destination.longitude},{destination.latitude}",
            "output": "json",
            "show_fields": "cost,polyline", # 显式请求 cost 和 polyline
        }
        
        if mode == "driving":
            params["strategy"] = "2" # 2: 距离优先（避免默认的速度优先导致绕路）
        
        if mode == "transit":
            # 公交路径规划需要城市信息
            # v5 接口参数是 city1 和 city2
            city1 = self._get_city_info(origin.latitude, origin.longitude)
            city2 = self._get_city_info(destination.latitude, destination.longitude)
            params["city1"] = city1
            params["city2"] = city2
            # v5 接口公交策略默认 0: 推荐模式
            params["strategy"] = "0" 
            
        try:
            print(f"Requesting Gaode API: {url} with params: {params}")
            response = requests.get(url, params=params)
            print(f"Gaode Response Status: {response.status_code}")
            try:
                print(f"Gaode Response Body: {response.text[:500].encode('utf-8', errors='ignore').decode('utf-8')}") 
            except Exception:
                print("Gaode Response Body: (Print failed)")
            
            data = response.json()
            
            # 检查 API 状态
            # status: 1 成功, 0 失败
            if data.get("status") != "1":
                # 记录详细错误信息
                infocode = data.get("infocode")
                info = data.get("info")
                print(f"Gaode API error: mode={mode}, infocode={infocode}, info={info}")
                return {}
            
            # 检查是否有路线数据
            # v5 接口返回 route 对象
            route = data.get("route")
            if not route:
                return {}

            result = {
                "origin": f"{origin.longitude},{origin.latitude}",
                "destination": f"{destination.longitude},{destination.latitude}",
                "paths": []
            }
            
            # 解析 paths
            # v5 接口:
            # driving/walking/bicycling -> route.paths
            # transit -> route.transits
            paths_data = []
            if mode == "transit":
                paths_data = route.get("transits", [])
            else:
                paths_data = route.get("paths", [])
                
            if not paths_data:
                return {}

            for p in paths_data:
                # 提取距离和耗时
                distance = float(p.get("distance", 0))
                
                # 提取耗时 (duration)
                # v5 接口: cost.duration 或 duration (取决于模式)
                duration = 0
                if "cost" in p and "duration" in p["cost"]:
                     duration = float(p["cost"]["duration"])
                elif "duration" in p: # transit 模式直接在 transit item 下
                     duration = float(p.get("duration", 0))
                
                # 提取 Polyline
                # v5 接口: 需要 show_fields=polyline 并在 steps/segments 中或者外层获取
                # 简化处理：这里暂不深度拼接 polyline，除非前端强需求
                # 如果 API 直接返回了 polyline (如 transit 的某些情况或 driving 的某些情况)，则使用
                # 注意：v5 文档显示 polyline 可能在 steps 中，需要拼接
                polyline = ""
                
                path_info = {
                    "distance": distance,
                    "duration": duration,
                    "steps": [],
                    "polyline": polyline 
                }
                
                # 简化步骤信息
                steps = []
                if mode == "transit":
                    steps = p.get("segments", [])
                else:
                    steps = p.get("steps", [])
                    
                path_info["steps"] = len(steps)
                result["paths"].append(path_info)
                
            return result
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
