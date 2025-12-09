修改整个项目的风格

查看别人主页，查看它们发布的帖子和公开的Trip，添加好友的功能

在社区的帖子种显示图片

在trip中添加一张图片

许多弹窗没有取消按钮，需要增加取消按钮

现在数据库中的一个帖子在社区动态中会显示两次


用户在trip中添加activity后，后台自动调用travel_sharing_app_v0\backend\src\app_travel\infrastructure\external_service\gaode_geo_service_impl.py计算路径时间的功能有问题，现在路径并不能计算出来，请修正


疑问：
1. 若要增加添加好友的功能，应该写在app_auth中吗？是否需要修改数据库范式？
2. 若在旅行界面，每个Trip可以添加一张图片，需要修改数据库范式吗？
3. 群聊中支持分享帖子吗？