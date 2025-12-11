

查看别人主页，查看它们发布的帖子和公开的Trip，添加好友的功能





客观地回答，不要附和我！！
app_admin的要求： 遵循领域驱动设计的原则，app_admin（travel_sharing_app_v0\backend\src\app_admin）作为一个限界上下文，是只有role为admin的用户使用的页面，负责管理数据库中的所有内容，要求能够对每一个表格进行增删改查操作。（总共有这些表格：activities、comments、conversation_participants、conversations、likes、messages、post_images、post_tags、posts、transits、trip_days、trip_members、users），要求在增和改某一行记录的时候，这行记录要符合各个PO中规定的类型和非空性约束。
那么，遵循最简原则（不要画蛇添足，这是个个人简单项目，如果某些部分是不必要的，你直接回答我不必要就可以了）：
1. app_admin的领域层中的聚合根、实体、值对象、领域服务和领域事件分别对应如何设计？
2. app_admin的领域层应当定义哪些需求方接口？
3. app_admin的基础设施层应实现什么？有必要有po、repository、dao吗？
4. app_admin的后端view应该像前端暴露哪些接口？
5. app_admin的前端应该有哪些页面？



增加管理员页面



1. 调整布局：在个人主页中，用户动态和旅行显示部分，一行显示两个动态/旅行（目前显示了三个，太密了）
2. admin的交通管理页面和活动管理页面出现错误：加载失败，似乎是因为从数据库中获取的字段与数据库表不匹配
3. 既然存在有post_images表，那么一个帖子应当可以有多个图片，而不是只有一个图片。
4. admin页面的配色保持和其它页面一致，同样使用 dark glassmorphism风格






一、增加好友关系：
1. 需要新增一张关联表（friendships），通常包含以下字段：
    - requester_id (申请人)
    - addressee_id (被申请人)
    - status (状态：pending/accepted/blocked)
    - created_at (创建时间)
2. 逻辑写在 app_social中
3. 当用户访问其他人的主页时，有一个“添加好友”按钮，点击后可以发送好友请求。在消息页面，用户可以查看所有好友请求和已接受的好友关系。
4. 在消息界面，每一个好友有一个单独的聊天窗口，用户可以在其中发送消息。（只有成为好友后才能聊天，在接受好友后，原来“接受好友”的界面变成聊天窗口）



二、若在旅行界面，每个 Trip 可以添加一张图片，需要修改数据库范式
1. backend/src/app_travel/infrastructure/database/persistent_model/trip_po.py中
2. 需要在 trips 表中增加一个字段，例如 cover_image_url (VARCHAR/String)，用于存储封面图片的链接。
3. 同时需要在 Trip 领域实体 ( trip_aggregate.py ) 和值对象中增加对应的属性。
4. 可能要修改 travel_sharing_app_v0\backend\src\shared\storage\local_file_storage.py 中的路径，与帖子的图片位置分离开

三、若要在群聊中分享帖子（用卡片形式的富文本来分析）
1. backend/src/app_social/domain/value_objects/social_value_objects.py 中的 MessageContent 类扩展 message_type 枚举，增加 post_share 类型
2. 在前后端增加相应的解析逻辑


我可以将所有的sqlalchemy_dao的实现修改为使用原始SQL，而功能不变吗？