import React, { useEffect, useState, useMemo } from 'react';
import { APILoader, Map, Marker, Polyline, ToolBarControl, ScaleControl, ControlBarControl } from '@uiw/react-amap';
import LoadingSpinner from '../../components/LoadingSpinner';

const TripMap = ({ activities = [], transits = [] }) => {
    // 1. 设置安全密钥 (必须在加载地图前设置)
    useEffect(() => {
        window._AMapSecurityConfig = {
            securityJsCode: import.meta.env.VITE_AMAP_SECURITY_CODE,
        };
    }, []);

    const [mapInstance, setMapInstance] = useState(null);
    const [aMapLoaded, setAMapLoaded] = useState(false);

    // 2. 准备标记点数据
    const markers = useMemo(() => {
        if (!aMapLoaded || !window.AMap) return [];
        
        return activities
            .filter(act => act.location && act.location.longitude && act.location.latitude)
            .map((act, index) => ({
                position: new window.AMap.LngLat(parseFloat(act.location.longitude), parseFloat(act.location.latitude)),
                title: act.name,
                label: {
                    content: `<div style="background-color: #3b82f6; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">${index + 1}</div>`,
                    direction: 'center', // 文本标注方位
                    offset: new window.AMap.Pixel(0, 0), // 偏移量
                },
                data: act
            }));
    }, [activities, aMapLoaded]);

    // 3. 准备路线数据
    const polylines = useMemo(() => {
        if (!aMapLoaded || !window.AMap) return [];

        return transits
            .filter(t => t.polyline)
            .map(t => {
                // 后端返回的 polyline 格式通常是 "lng,lat;lng,lat" 字符串
                const path = t.polyline.split(';').map(pointStr => {
                    const [lng, lat] = pointStr.split(',');
                    return new window.AMap.LngLat(parseFloat(lng), parseFloat(lat));
                });
                
                return {
                    path,
                    mode: t.mode,
                    strokeStyle: t.mode === 'walking' ? 'dashed' : 'solid',
                    strokeColor: '#3b82f6'
                };
            });
    }, [transits, aMapLoaded]);

    // 4. 计算初始中心点
    const initialCenter = useMemo(() => {
        if (activities.length > 0 && activities[0].location) {
             const { longitude, latitude } = activities[0].location;
             if (longitude && latitude) {
                 const lng = parseFloat(longitude);
                 const lat = parseFloat(latitude);
                 if (!isNaN(lng) && !isNaN(lat)) {
                     return [lng, lat];
                 }
             }
        }
        return undefined;
    }, [activities]);

    // 监听 initialCenter 变化并更新地图中心
    useEffect(() => {
        if (mapInstance && initialCenter) {
            mapInstance.setCenter(initialCenter);
        }
    }, [mapInstance, initialCenter]);

    // 暴露给测试环境 (E2E)
    useEffect(() => {
        if (import.meta.env.MODE === 'test' || import.meta.env.DEV) {
            window.__TEST_MAP_INSTANCE__ = mapInstance;
            window.__TEST_MARKERS__ = markers;
            window.__TEST_POLYLINES__ = polylines;
        }
    }, [mapInstance, markers, polylines]);

    // 5. 自动缩放视野以包含所有标记和路线
    useEffect(() => {
        if (mapInstance && aMapLoaded && (markers.length > 0 || polylines.length > 0)) {
             // 使用 setFitView 自动适配
             // 注意：React-AMap 的 Map 组件会在子组件加载完成后自动处理，
             // 但为了保险起见，我们也可以手动调用 mapInstance.setFitView()
             // 这里我们依赖 Map 组件的子组件渲染，稍微延迟一下确保 marker 已经挂载
             setTimeout(() => {
                 try {
                     mapInstance.setFitView(null, false, {
                         padding: [50, 50, 50, 50]
                     });
                 } catch (e) {
                     console.warn("FitView failed", e);
                 }
             }, 800);
        }
    }, [mapInstance, markers, polylines, aMapLoaded]);

    return (
        <div style={{ width: '100%', height: '600px', borderRadius: '0.5rem', overflow: 'hidden', border: '1px solid #e2e8f0' }}>
            <APILoader 
                akey={import.meta.env.VITE_AMAP_KEY}
                onComplete={() => setAMapLoaded(true)}
            >
                <Map
                    onInstanceCreated={setMapInstance}
                    zoom={11} // 初始缩放
                    center={initialCenter}
                >
                    <ScaleControl offset={[16, 30]} position="LB" />
                    <ToolBarControl offset={[16, 10]} position="RB" />
                    <ControlBarControl offset={[16, 180]} position="RB" />

                    {markers.map((marker, idx) => (
                        <Marker
                            key={`marker-${idx}`}
                            position={marker.position}
                            title={marker.title}
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
                            showDir={true} // 显示箭头
                        />
                    ))}
                </Map>
            </APILoader>
        </div>
    );
};

export default TripMap;
