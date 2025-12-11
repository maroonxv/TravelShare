修改整个项目的风格

查看别人主页，查看它们发布的帖子和公开的Trip，添加好友的功能


在trip中添加一张图片


1. 在trip_detail页面的activity之间的交通方式显示得大一点，字体用更显眼一点的灰色（交通费和邮费的字体颜色很好，但是交通方式及时间的字体的明度再提高一点）
2. 帖子的评论不能显示评论者的昵称和头像。这里要显示，并且点击评论者的昵称和头像要跳转到它的个人主页
3. 把trip_detail页面显示的每个activity的开始时间显示得大一点，同时增加显示每个activity的结束时间
4. 在 trip_detail页面点击某一个activity，进到修改activity的弹窗中，保存修改时会提示“修改活动失败”。另外，这里要添加一个判断逻辑：若修改的结束时间早于开始时间，则提示“结束时间不能早于开始时间”；若修改的结束时间晚于后一个activity的开始时间，则可以保存成功，但是在trip_detail页面应当用红色显示后一个activity的开始时间，旁边写上小字提醒“时间冲突”



任务：
1. 帖子关联的旅行在社区和帖子详情页还是没有显示出来！把它显示出来，并且若该旅行是公开的，点击它可以跳转到该旅行的详情页
2. 旅行的admin可以在trip_detail页面修改该旅行的可见性
3. 为trip表增加一个字段cover_image_url，用于存储这个trip的封面图片（而且你告诉了我如果这张图片只隶属于这个trip 的 id的话，不用把trip表现有的数据删掉对吧）。
4. 增加功能：每一个trip的admin用户在创建trip时，可以上传一张图片作为该trip的封面图片，调用 travel_sharing_app_v0\backend\src\shared\storage\local_file_storage.py ，把这张封面图片保存到 D:\学业\CODE_PROJECTS\Trae\数据库及计网课设\travel_sharing\travel_sharing_app_v0\backend\src\static\uploads\trip_covers 目录下
5. 为旅行的admin在trip_detail页面增加一个编辑旅行按钮，admin用户点击后有一个弹窗，可以编辑这个旅行的信息


任务：
1. 将trip的封面图片显示在“旅行”页面和trip_detail页面。其中，关于封面图片在trip_detail页面的显示，你可以发挥想象力做得美观一点
2. 在社区页面的帖子上，若是自己点过赞的，把赞显示为红色（现在刚刚点赞时是红色的，但是刷新页面后就不是红色的了）
3. 现在点击帖子关联的旅行后，没有跳转到对应的trip_detail页面，而是跳转回社区页面了，这里不对，请修正



客观地回答，不要附和我！！
app_admin的要求： 遵循领域驱动设计的原则，app_admin（travel_sharing_app_v0\backend\src\app_admin）作为一个限界上下文，是只有role为admin的用户使用的页面，负责管理数据库中的所有内容，要求能够对每一个表格进行增删改查操作。（总共有这些表格：activities、comments、conversation_participants、conversations、likes、messages、post_images、post_tags、posts、transits、trip_days、trip_members、users），要求在增和改某一行记录的时候，这行记录要符合各个PO中规定的类型和非空性约束。
那么，遵循最简原则（不要画蛇添足，这是个个人简单项目，如果某些部分是不必要的，你直接回答我不必要就可以了）：
1. app_admin的领域层中的聚合根、实体、值对象、领域服务和领域事件分别对应如何设计？
2. app_admin的领域层应当定义哪些需求方接口？
3. app_admin的基础设施层应实现什么？有必要有po、repository、dao吗？
4. app_admin的后端view应该像前端暴露哪些接口？
5. app_admin的前端应该有哪些页面？



增加管理员页面


用户在trip中添加activity后，后台自动调用travel_sharing_app_v0\backend\src\app_travel\infrastructure\external_service\gaode_geo_service_impl.py计算路径时间的功能有问题，现在路径并不能计算出来，请修正


我有一个任务和三个疑问。请你完成任务，但是对于三个问题，只需要回答不需要改代码：
任务：
一旦某个帖子有评论，点进帖子详情页面就会出现bug，什么都显示不出来

疑问：
1. 现在user表中有一个role字段，用于存储user或者admin身份，但是现在项目没有管理员页面。若要增加一个管理员页面专门用来管理数据库中的所有内容，我需要增加一个新的app（app_admin）吗？因为根据领域驱动设计的原则，管理员的功能属于一个独立的限界上下文吗？
2. 若要给每个trip添加一个封面图片，需要修改数据库范式吗？
3. 若要修改数据库某个表格的范式，我就先把原有表格的数据删除，然后要怎么做？（我可以直接丢弃原来的数据，因为还处于开发阶段）


一、增加好友关系：
1. 需要新增一张关联表（friendships），通常包含以下字段：
    - requester_id (申请人)
    - addressee_id (被申请人)
    - status (状态：pending/accepted/blocked)
    - created_at (创建时间)
2. 逻辑写在 app_social中

二、若在旅行界面，每个 Trip 可以添加一张图片，需要修改数据库范式
1. backend/src/app_travel/infrastructure/database/persistent_model/trip_po.py中
2. 需要在 trips 表中增加一个字段，例如 cover_image_url (VARCHAR/String)，用于存储封面图片的链接。
3. 同时需要在 Trip 领域实体 ( trip_aggregate.py ) 和值对象中增加对应的属性。
4. 可能要修改 travel_sharing_app_v0\backend\src\shared\storage\local_file_storage.py 中的路径，与帖子的图片位置分离开

三、若要在群聊中分享帖子（用卡片形式的富文本来分析）
1. backend/src/app_social/domain/value_objects/social_value_objects.py 中的 MessageContent 类扩展 message_type 枚举，增加 post_share 类型
2. 在前后端增加相应的解析逻辑


我可以将所有的sqlalchemy_dao的实现修改为使用原始SQL，而功能不变吗？