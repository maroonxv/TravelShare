后续步骤



3. 使用 Alembic 创建数据库迁移

4. 添加 init.py exports 以方便导入








根据travel_sharing_app_v0\README.md中项目描述以及app_social的领域层travel_sharing_app_v0\backend\src\app_social\domain、app_social的基础设施层travel_sharing_app_v0\backend\src\app_social\infrastructure，在travel_sharing_app_v0\backend\src\app_social\services\social_service.py中编写app_social的应用层；在travel_sharing_app_v0\backend\src\app_social\view\social_view.py中编写app_social的接口层

一、应用层应当至少实现以下要点。其它要点你可以发挥想象力进行补充：
  1. 事务边界与生命周期管理（领域层只管修改内存中的对象，应用层负责调用Repository把这些修改变成数据库里的永久记录）
  2. 领域对象的“加载-执行-保存”循环：a. 调用 IPostRepository、IConversationRepository，将持久化模型转化为领域模型 b. 调用聚合根、领域服务的方法进行业务逻辑处理 c. 调用 IPostRepository、IConversationRepository，将领域模型转化为持久化模型 
  3. 将聚合根中记录的领域事件发布到事件总线 EventBus
  4. 在事务结束后统一调用数据库的commit（而不是在DAO中调用）

二、接口层应当至少实现以下要点。其它要点你可以发挥想象力进行补充：
  0. 使用RESTful API与React.js前端进行交互
  1. 接收HTTP请求，解析参数，调用应用层服务进行业务逻辑处理
  2. 将应用层返回的结果封装为HTTP响应，返回给客户端
  3. 处理异常情况，返回适当的HTTP状态码和错误信息