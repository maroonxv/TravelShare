后续步骤



3. 使用 Alembic 创建数据库迁移

4. 添加 init.py exports 以方便导入



1. 在 transit.py（现在为空）中建立表示“移动“的实体，在transit_value_objects.py（现在为空）中建立Transit实体所依赖的值对象。在 trip_day_entity.py 中增加用于存储Activities之间的Transit的属性。Activity之间、Transit之间以及Activity和Transit之间的先后顺序要清楚表示。

2. 在itinerary_service.py（现在为空）中编写一个领域服务，作为“智能行程管家” ，具有以下职责：
    - 接收一个Activity的列表，计算两两Activity之间的最佳路径（默认用driving计算），返回值应当与 TripDay 实体中存储Activity 与 Transit 的逻辑相匹配。
    - 接收一个模糊的地名，调用IGeoService.geocode获取精确的坐标和标准地址
    - 检查行程是否不可行：例如活动 A 结束时间 10:00，活动 B 开始时间 10:10，但路程需要 30 分钟 -> 报警

3. 在 Trip聚合根中，
    - add_activity()中，添加了一个Activity之后，要能调用ItineraryService计算新加的Activity与前一个Activity之间的最佳路径（默认用driving计算）
    - update_day_itinerary()中，一次性添加一天的所有Activity之后，要能调用ItineraryService计算所有Activity之间的最佳路径（默认用driving计算）

4. 在Trip聚合根中把add_activity()和modify_activity()分开来。一个Activity被修改后，应当调用ItineraryService把前一个Activity与该Activity间的Transit、该Activity与后一个Activity间的Transit都重新计算（默认用driving计算）

5. 生成整个旅行的统计报表：
    1. 总里程、总游玩时间、总交通时间。
    2. 打卡地图（所有去过的城市的点）。
    3. 预估总花费（包含预估的交通费）。