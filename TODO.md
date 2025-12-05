

我在搭建如下描述的项目：


后端采用 Flask框架，我已经创建了三个app：app_auth, app_travel和app_social（这三个app就是三个限界上下文）
每个app内部采用领域驱动设计的原则编排，采用事件驱动架构组织，在存储上采用Repository+DAO模式
秉持最简原则，请帮我完善：
0. 三个app的实体、值对象、聚合根、领域服务的属性与方法
1. 三个app的实体、值对象、聚合根、领域服务之间的依赖/组合关系
2. 三个app的domain_event，使得它们足够这个限界上下文内部以及限界上下文之间进行交互，在聚合根中保存领域事件队伍（稍后由应用层发布到事件总线，但是这个现在暂时不着急）
3. event_handler目录下的不同event_handler，（这里是重点，你要先告诉我你准备创建几个event handler，以及为什么这样划分）
4. 三个app的domain_interface中定义的repository接口以及外部服务接口。这些接口被聚合根、领域服务或者领域层外的应用层调用。

注意领域服务保持无状态，聚合根尽可能“厚”，使得整个建模是充血模型而不是贫血模型

write up an execution documentation first