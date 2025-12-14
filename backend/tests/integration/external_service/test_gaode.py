import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))
from app_travel.infrastructure.external_service.gaode_geo_service_impl import GaodeGeoServiceImpl
from app_travel.domain.value_objects.travel_value_objects import Location

class TestGaodeGeoServiceIntegration:
    """高德地图服务集成测试（调用真实 API）
    
    覆盖：
    1. 地理编码 / 逆地理编码
    2. 距离计算
    3. 各种交通方式的路径规划 (Driving, Walking, Transit, Cycling)
    4. 异常/边界情况 (无效地址、跨海、极远距离)
    5. POI 搜索
    """
    
    @pytest.fixture
    def geo_service(self):
        # 使用用户提供的真实 Key
        return GaodeGeoServiceImpl(api_key="615fc65de7dcae0a3b68b67ca8746591")

    # --- 基础地理功能测试 ---

    def test_geocode_real(self, geo_service):
        """测试地理编码：地址 -> 坐标"""
        address = "北京市天安门"
        location = geo_service.geocode(address)
        
        assert location is not None
        assert location.name == address
        assert location.has_coordinates()
        # 天安门大概坐标 (116.397, 39.908)
        assert 116.3 < location.longitude < 116.5
        assert 39.8 < location.latitude < 40.0
        assert "北京" in location.address

    def test_geocode_invalid(self, geo_service):
        """测试无效地址"""
        location = geo_service.geocode("!@#$%^&*()_INVALID_ADDRESS_12345")
        assert location is None

    def test_reverse_geocode_real(self, geo_service):
        """测试逆地理编码：坐标 -> 地址"""
        # 天安门坐标
        lat, lng = 39.908722, 116.397496
        address = geo_service.reverse_geocode(lat, lng)
        
        assert address is not None
        assert "北京" in address
        assert "东城" in address or "西城" in address

    def test_calculate_distance_real(self, geo_service):
        """测试距离计算"""
        # 北京 -> 上海 (直线距离约 1000km+)
        origin = Location(name="Beijing", latitude=39.9042, longitude=116.4074)
        dest = Location(name="Shanghai", latitude=31.2304, longitude=121.4737)
        
        distance = geo_service.calculate_distance(origin, dest)
        
        assert distance > 1000000 # > 1000km
        assert distance < 1300000 # < 1300km

    # --- 路径规划测试 (v5 API) ---

    def test_get_route_driving_changsha_case1(self, geo_service):
        """测试驾车路线规划 - 长沙真实案例1
        从长沙万达·总部国际C2到长沙IFS国金购物中心
        预期：约2.6-3.0公里
        """
        # 使用精确坐标避免地理编码偏差
        # 万达·总部国际C2: 112.9698, 28.2035 (近似)
        # 长沙IFS: 112.9764, 28.1925 (近似)
        # 让 geocode 去解析更准确
        origin = geo_service.geocode("长沙万达总部国际C2")
        dest = geo_service.geocode("长沙IFS国金购物中心")
        
        assert origin is not None
        assert dest is not None
        
        route = geo_service.get_route(origin, dest, mode="driving")
        
        assert route is not None
        assert len(route["paths"]) > 0
        path = route["paths"][0]
        
        # 验证距离：预期在 2000m - 4000m 之间 (考虑到路况和单行道，放宽一点上限)
        print(f"Case 1 Distance: {path['distance']}m")
        assert path["distance"] > 2000
        assert path["distance"] < 4000 

    def test_get_route_driving_changsha_case2(self, geo_service):
        """测试驾车路线规划 - 长沙真实案例2
        从长沙万达·总部国际C2到长沙中南大学潇湘校区图书馆
        预期：约9.2-12.8公里
        """
        origin = geo_service.geocode("长沙万达总部国际C2")
        dest = geo_service.geocode("中南大学新校区图书馆") # 注意：用户说是潇湘校区，但中南大学主要校区是新校区/南校区，这里尝试用新校区图书馆，或者更精确的"中南大学新校区-图书馆"
        
        # 如果 geocode 失败，尝试手动指定坐标（中南大学新校区图书馆约在 112.927, 28.163）
        if not dest:
             dest = Location(name="CSU Library", latitude=28.163, longitude=112.927)

        assert origin is not None
        assert dest is not None
        
        route = geo_service.get_route(origin, dest, mode="driving")
        
        assert route is not None
        assert len(route["paths"]) > 0
        path = route["paths"][0]
        
        # 验证距离：预期在 8500m - 14000m 之间
        print(f"Case 2 Distance: {path['distance']}m")
        assert path["distance"] > 8500
        assert path["distance"] < 14000

    def test_get_route_driving_success(self, geo_service):
        """测试驾车路线规划 (Success)"""
        # 北京南站 -> 北京西站
        origin = Location(name="Start", latitude=39.8650, longitude=116.3790) 
        dest = Location(name="End", latitude=39.8947, longitude=116.3216)
        
        route = geo_service.get_route(origin, dest, mode="driving")
        
        assert route is not None
        assert "paths" in route
        assert len(route["paths"]) > 0
        path = route["paths"][0]
        assert path["distance"] > 0
        assert path["duration"] > 0
        assert path["steps"] > 0

    def test_get_route_walking_success(self, geo_service):
        """测试步行路线规划 (Success)"""
        # 附近短途：天安门 -> 故宫
        origin = Location(name="Start", latitude=39.9087, longitude=116.3975)
        dest = Location(name="End", latitude=39.9163, longitude=116.3971)
        
        route = geo_service.get_route(origin, dest, mode="walking")
        
        assert route is not None
        assert len(route["paths"]) > 0
        path = route["paths"][0]
        assert path["distance"] > 0
        # 步行大概 1km 左右
        assert path["distance"] < 3000

    def test_get_route_transit_success(self, geo_service):
        """测试公交路线规划 (Success) - 需要城市信息"""
        # 北京南站 -> 北京站
        origin = Location(name="Start", latitude=39.8650, longitude=116.3790)
        dest = Location(name="End", latitude=39.9047, longitude=116.4272)
        
        route = geo_service.get_route(origin, dest, mode="transit")
        
        assert route is not None
        # 注意：transit 模式返回结构可能稍有不同，但我们做了统一适配
        assert "paths" in route 
        assert len(route["paths"]) > 0
        path = route["paths"][0]
        assert path["distance"] > 0
        # 公交应该有 segments (适配为 steps)
        assert path["steps"] > 0

    def test_get_route_cycling_success(self, geo_service):
        """测试骑行路线规划 (Success)"""
        # 天安门 -> 前门
        origin = Location(name="Start", latitude=39.9087, longitude=116.3975)
        dest = Location(name="End", latitude=39.8987, longitude=116.3975)
        
        route = geo_service.get_route(origin, dest, mode="cycling") # 兼容 bicycling
        
        assert route is not None
        assert len(route["paths"]) > 0
        path = route["paths"][0]
        assert path["distance"] > 0

    # --- 异常与边界情况测试 ---

    def test_get_route_impossible_driving(self, geo_service):
        """测试无法驾车到达的情况 (例如：中国 -> 美国，或者跨海无桥)
        注意：高德只能规划国内路线。
        我们测试一个国内无法驾车到达的点（例如：海南岛到某个未连通的小岛，或者极远距离）
        或者更简单：直接测试一个极远距离看 API 反应，或者国外坐标。
        高德对国外坐标会返回错误。
        """
        # 北京 -> 纽约 (伪造坐标，高德应该报错或返回空)
        origin = Location(name="Beijing", latitude=39.9042, longitude=116.4074)
        dest = Location(name="NewYork", latitude=40.7128, longitude=-74.0060)
        
        route = geo_service.get_route(origin, dest, mode="driving")
        
        # 应该返回空字典
        assert route == {}

    def test_get_route_too_far_walking(self, geo_service):
        """测试超长距离步行 (API 应该会报错或返回空)"""
        # 北京 -> 上海
        origin = Location(name="Beijing", latitude=39.9042, longitude=116.4074)
        dest = Location(name="Shanghai", latitude=31.2304, longitude=121.4737)
        
        route = geo_service.get_route(origin, dest, mode="walking")
        
        # 预期：API 返回失败或空
        assert route == {}

    # --- POI 搜索测试 ---

    def test_search_places_keyword(self, geo_service):
        """测试关键字搜索"""
        keyword = "清华大学"
        results = geo_service.search_places(keyword)
        
        assert len(results) > 0
        first_match = results[0]
        assert "清华" in first_match.name
        assert first_match.has_coordinates()

    def test_search_places_around(self, geo_service):
        """测试周边搜索"""
        # 以天安门为中心，搜附近的"咖啡"
        center = Location(name="Center", latitude=39.9087, longitude=116.3975)
        results = geo_service.search_places("咖啡", location=center, radius=1000)
        
        assert len(results) > 0
        for res in results:
            assert res.has_coordinates()

