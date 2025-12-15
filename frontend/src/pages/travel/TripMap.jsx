import React, { useEffect, useState, useMemo } from 'react';
import { APILoader, Map, Marker, Polyline, ToolBarControl, ScaleControl, ControlBarControl } from '@uiw/react-amap';
import LoadingSpinner from '../../components/LoadingSpinner';

// Configure Security Code globally before component mounts
if (typeof window !== 'undefined') {
    window._AMapSecurityConfig = {
        securityJsCode: import.meta.env.VITE_AMAP_SECURITY_CODE,
    };
    console.log('AMap Security Config set');
}

const TripMap = ({ activities = [], transits = [], initialCenter }) => {
    // 状态管理
    const [map, setMap] = useState(null); // 地图实例
    const [center, setCenter] = useState(initialCenter || [116.397428, 39.90923]); // 默认北京
    const [zoom, setZoom] = useState(initialCenter ? 12 : 11);
    const [isTestMode, setIsTestMode] = useState(false);

    // 监听 initialCenter 变化
    useEffect(() => {
        if (initialCenter && initialCenter.length === 2) {
            console.log('Updating center from prop:', initialCenter);
            setCenter(initialCenter);
            setZoom(12);
        }
    }, [initialCenter]);

    // 检测测试环境
    useEffect(() => {
        const isTest = window.__TEST_MODE__ || import.meta.env.MODE === 'test' || 
                      (typeof window !== 'undefined' && window.navigator && window.navigator.userAgent && window.navigator.userAgent.includes('HeadlessChrome'));
        
        if (isTest) {
            setIsTestMode(true);
            console.log('Test Mode detected');
            // Mock AMap for test mode
            if (!window.AMap) {
                window.AMap = {
                    LngLat: class {
                        constructor(lng, lat) { this.lng = lng; this.lat = lat; }
                        getLng() { return this.lng; }
                        getLat() { return this.lat; }
                        toString() { return `${this.lng},${this.lat}`; }
                    },
                    Pixel: class { constructor(x, y) { this.x = x; this.y = y; } }
                };
            }
        }
    }, []);

    // 1. 计算初始中心点 (已改为由后端传递 initialCenter，此处仅作为兜底)
    const firstValidActivity = useMemo(() => {
        // 如果已经通过 props 传了 initialCenter，这里可以不再计算
        // 或者保留作为 fallback
        return activities.find(
            (act) => 
                act?.location?.longitude != null && 
                act?.location?.latitude != null && 
                !isNaN(parseFloat(act.location.longitude)) && 
                !isNaN(parseFloat(act.location.latitude))
        );
    }, [activities]);

    // 2. 当找到有效点时，更新中心点 (仅当没有 initialCenter 时启用)
    useEffect(() => {
        if (initialCenter) return; // 优先使用后端给的中心点
        if (!firstValidActivity) return;
        
        const lng = parseFloat(firstValidActivity.location.longitude);
        const lat = parseFloat(firstValidActivity.location.latitude);
        
        console.log('Updating map center to (calculated):', lng, lat);
        setCenter([lng, lat]);
        setZoom(12);
    }, [firstValidActivity, initialCenter]);

    // 3. 监听 center/map 变化并手动更新地图实例
    // 确保地图实例加载完成且中心点变化时，强制 setCenter
    useEffect(() => {
        if (!map) return;
        console.log('Manually setting center via map instance:', center);
        map.setCenter(center);
    }, [map, center]);

    // 4. 准备标记点数据
    const markers = useMemo(() => {
        return activities
            .filter(act => act.location && act.location.longitude && act.location.latitude)
            .map((act, index) => ({
                position: [parseFloat(act.location.longitude), parseFloat(act.location.latitude)], // 使用数组格式
                title: act.name,
                data: act
            }));
    }, [activities]);

    // 5. 准备路线数据
    const polylines = useMemo(() => {
        return transits
            .filter(t => t.polyline)
            .map(t => {
                const path = t.polyline.split(';').map(pointStr => {
                    const [lng, lat] = pointStr.split(',');
                    return [parseFloat(lng), parseFloat(lat)]; // 使用数组格式
                });
                
                return {
                    path,
                    mode: t.mode,
                    strokeStyle: t.mode === 'walking' ? 'dashed' : 'solid',
                    strokeColor: '#3b82f6'
                };
            });
    }, [transits]);

    // 6. 自动缩放视野 (已移除，避免覆盖 center 设置)
    /*
    useEffect(() => {
        if (map && (markers.length > 0 || polylines.length > 0)) {
             // 延迟一下确保 marker 已渲染
             setTimeout(() => {
                 try {
                     map.setFitView(null, false, {
                         padding: [50, 50, 50, 50]
                     });
                 } catch (e) {
                     console.warn("FitView failed", e);
                 }
             }, 800);
        }
    }, [map, markers, polylines]);
    */

    // 暴露给测试环境
    useEffect(() => {
        if (map) {
            window.__TEST_MAP_INSTANCE__ = map;
            window.__TEST_MARKERS__ = markers;
            window.__TEST_POLYLINES__ = polylines;
        }
    }, [map, markers, polylines]);


    if (isTestMode) {
        return (
            <div 
                data-testid="trip-map-container"
                style={{ width: '100%', height: '600px', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#e2e8f0' }}
            >
                <div>Mock Map Mode Active</div>
            </div>
        );
    }

    return (
        <div data-testid="trip-map-container" style={{ width: '100%', height: '600px', borderRadius: '0.5rem', overflow: 'hidden', border: '1px solid #e2e8f0', position: 'relative' }}>
            <APILoader akey={import.meta.env.VITE_AMAP_KEY}>
                <Map
                    zoom={zoom}
                    center={center}
                    viewMode="2D"
                    ref={(instance) => {
                        if (instance && instance.map && instance.map !== map) {
                            console.log('Map Instance acquired via ref callback');
                            setMap(instance.map);
                        }
                    }}
                >
                    <ScaleControl offset={[16, 30]} position="LB" />
                    <ToolBarControl offset={[16, 10]} position="RB" />
                    <ControlBarControl offset={[16, 180]} position="RB" />

                    {markers.map((marker, idx) => (
                        <Marker
                            key={`marker-${idx}`}
                            position={marker.position}
                            title={marker.title}
                            offset={window.AMap ? new window.AMap.Pixel(-14, -14) : [-14, -14]} // 中心对齐调整 (28px/2)
                        >
                            <div style={{
                                position: 'relative',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center'
                            }}>
                                <div style={{
                                    backgroundColor: '#3b82f6',
                                    color: 'white',
                                    borderRadius: '50%',
                                    width: '28px',
                                    height: '28px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontWeight: 'bold',
                                    border: '2px solid white',
                                    boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
                                    zIndex: 10
                                }}>
                                    {idx + 1}
                                </div>
                                <div style={{
                                    backgroundColor: 'white',
                                    padding: '4px 8px',
                                    borderRadius: '4px',
                                    fontSize: '12px',
                                    fontWeight: '500',
                                    marginTop: '4px',
                                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                                    whiteSpace: 'nowrap',
                                    color: '#1e293b'
                                }}>
                                    {marker.title}
                                </div>
                            </div>
                        </Marker>
                    ))}

                    {polylines.map((line, idx) => (
                        <Polyline
                            key={`line-${idx}`}
                            path={line.path}
                            strokeColor={line.strokeColor}
                            strokeWeight={6}
                            strokeStyle={line.strokeStyle}
                            strokeOpacity={0.8}
                            showDir={true}
                        />
                    ))}
                </Map>
            </APILoader>
        </div>
    );
};

export default TripMap;
