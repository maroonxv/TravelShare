import sys
import os
import random
import uuid
from datetime import datetime, timedelta, date, time
import json

# Add backend/src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
backend_src = os.path.join(backend_dir, 'src')
sys.path.append(backend_src)
print(f"Added {backend_src} to sys.path")

from app import create_app
from shared.database.core import engine, SessionLocal, Base
from app_auth.infrastructure.external_service.password_hasher_impl import PasswordHasherImpl
from app_auth.domain.value_objects.user_value_objects import Password, UserRole
from app_social.domain.value_objects.friendship_value_objects import FriendshipStatus
from app_social.domain.value_objects.social_value_objects import PostVisibility, ConversationType, ConversationRole
from app_travel.domain.value_objects.travel_value_objects import TripStatus, TripVisibility, MemberRole

# Import POs
from app_auth.infrastructure.database.persistent_model.user_po import UserPO
from app_social.infrastructure.database.persistent_model.post_po import PostPO, CommentPO, LikePO, PostImagePO, PostTagPO
from app_social.infrastructure.database.persistent_model.conversation_po import ConversationPO, conversation_participants
from app_social.infrastructure.database.persistent_model.message_po import MessagePO
from app_social.infrastructure.database.po.friendship_po import FriendshipPO
from app_travel.infrastructure.database.persistent_model.trip_po import TripPO, TripMemberPO, TripDayPO, ActivityPO, TransitPO
from app_ai.infrastructure.database.persistent_model.ai_po import AiConversationPO, AiMessagePO

def generate_uuid():
    return str(uuid.uuid4())

def init_data():
    print("Initializing database with mock data...")
    session = SessionLocal()
    hasher = PasswordHasherImpl()
    
    try:
        # 1. Clear existing data
        print("Cleaning up old data...")
        session.query(AiMessagePO).delete()
        session.query(AiConversationPO).delete()
        session.query(PostImagePO).delete()
        session.query(PostTagPO).delete()
        session.query(CommentPO).delete()
        session.query(LikePO).delete()
        session.query(PostPO).delete()
        session.query(MessagePO).delete()
        session.execute(conversation_participants.delete())
        session.query(ConversationPO).delete()
        session.query(FriendshipPO).delete()
        session.query(ActivityPO).delete()
        session.query(TransitPO).delete()
        session.query(TripDayPO).delete()
        session.query(TripMemberPO).delete()
        session.query(TripPO).delete()
        session.query(UserPO).delete()
        session.commit()

        # 2. Create Users
        print("Creating users...")
        users = []
        user_data = [
            {"username": "travel_lover", "email": "lover@test.com", "bio": "热爱旅行，走遍世界", "location": "Beijing"},
            {"username": "photo_master", "email": "photo@test.com", "bio": "用镜头记录美好", "location": "Shanghai"},
            {"username": "foodie_jenny", "email": "jenny@test.com", "bio": "唯有美食与爱不可辜负", "location": "Guangzhou"},
            {"username": "backpacker_tom", "email": "tom@test.com", "bio": "穷游背包客", "location": "Shenzhen"},
            {"username": "nature_hiker", "email": "hiker@test.com", "bio": "大自然搬运工", "location": "Chengdu"},
            {"username": "city_walker", "email": "walker@test.com", "bio": "城市漫步者", "location": "Hangzhou"},
            {"username": "history_buff", "email": "history@test.com", "bio": "追寻历史的足迹", "location": "Xi'an"},
            {"username": "beach_boy", "email": "beach@test.com", "bio": "阳光沙滩海浪", "location": "Sanya"},
        ]

        default_password = hasher.hash(Password("password123"))

        for data in user_data:
            user = UserPO(
                id=generate_uuid(),
                username=data["username"],
                email=data["email"],
                hashed_password=default_password.value,
                bio=data["bio"],
                location=data["location"],
                is_active=True,
                is_email_verified=True,
                role=UserRole.USER.value,
                created_at=datetime.utcnow()
            )
            session.add(user)
            users.append(user)
        
        session.commit()
        print(f"Created {len(users)} users.")

        # 3. Create Friendships
        print("Creating friendships...")
        existing_pairs = set()

        def add_friendship(requester_id, addressee_id, status):
            pair = (requester_id, addressee_id)
            if pair in existing_pairs:
                return
            
            f = FriendshipPO(id=generate_uuid(), requester_id=requester_id, addressee_id=addressee_id, status=status)
            session.add(f)
            existing_pairs.add(pair)

        for i in range(len(users)):
            next_user = users[(i + 1) % len(users)]
            add_friendship(users[i].id, next_user.id, FriendshipStatus.ACCEPTED)
            
            prev_user = users[(i - 1) % len(users)]
            add_friendship(users[i].id, prev_user.id, FriendshipStatus.ACCEPTED)
            
            rand_user = random.choice(users)
            if rand_user.id != users[i].id:
                 add_friendship(users[i].id, rand_user.id, FriendshipStatus.PENDING)

        session.commit()

        # 4. Create Posts
        print("Creating posts...")
        
        # Define detailed post data
        destinations = [
            # Changsha
            {
                "image": "changsha_aiwan_pavillion.jpg",
                "title": "爱晚亭的深秋：停车坐爱枫林晚",
                "text": "“停车坐爱枫林晚，霜叶红于二月花。” 千年前杜牧的一首诗，让爱晚亭成为了多少文人墨客心中的圣地。今天终于有机会亲自来到这里，感受深秋的韵味。走进岳麓山，沿着蜿蜒的山路而上，远远地就能看到那座古朴典雅的亭子掩映在万山红遍之中。\n\n现在的季节正是赏枫的最佳时节，漫山遍野的红叶如火如荼，层林尽染，在阳光的照耀下显得格外艳丽。爱晚亭的琉璃碧瓦与四周的红叶相互映衬，构成了一幅绝美的中国山水画。亭内有毛主席亲笔题写的匾额，更增添了一份厚重的历史感。坐在这里，听着风吹过树叶的沙沙声，看着眼前这醉人的景色，仿佛时间都静止了。虽然游客不少，但依然能感受到那份独特的宁静与诗意。强烈推荐大家在这个季节来打卡！#长沙 #岳麓山 #爱晚亭 #赏枫 #秋天",
                "comments": [
                    "这红叶也太美了吧！真的像画一样。",
                    "杜牧的诗意境全出来了，博主拍得真好。",
                    "现在去人多吗？想周末去看看。",
                    "爱晚亭确实是长沙必去的地方，尤其是秋天。",
                    "感觉隔着屏幕都能闻到秋天的味道。",
                    "照片色调很舒服，是用什么相机拍的呀？"
                ]
            },
            {
                "image": "changsha_central_south_university.jpeg",
                "title": "漫步中南大学：重返十八岁的校园时光",
                "text": "今天特意来打卡了中南大学，一进校门就被那种浓厚的学术氛围感染了。校园非常大，绿树成荫，古朴的教学楼和现代化的实验室错落有致。走在宽阔的林荫大道上，看着抱着书本匆匆走过的学生，听着操场上远处传来的欢呼声，仿佛瞬间穿越回了自己的学生时代。\n\n特别喜欢校园里的那些老建筑，红砖墙面在阳光下显得格外有质感，每一块砖瓦似乎都在诉说着学校的历史。我们在校园里漫无目的地闲逛，路过了著名的和平楼、民主楼，还在食堂蹭了一顿饭，味道真的很不错，而且价格便宜到让人感动！如果你也怀念校园时光，不妨来中南大学走走，这里的青春气息一定能治愈你。#中南大学 #校园时光 #青春 #长沙高校 #怀旧",
                "comments": [
                    "哇，是我的母校！好怀念啊。",
                    "中南的食堂确实好吃，尤其是二食堂。",
                    "那几栋老建筑真的很有味道，拍照很出片。",
                    "看到学弟学妹们，感觉自己都变年轻了。",
                    "博主拍出了中南的气质，低调而有内涵。",
                    "下次去长沙一定要去中南转转。"
                ]
            },
            {
                "image": "changsha_central_south_university_library.jpeg",
                "title": "知识的殿堂：中南大学图书馆打卡",
                "text": "一座大学的灵魂往往在于它的图书馆。中南大学的新校区图书馆真的非常宏伟壮观，远远望去就像一本展开的巨书，寓意着开卷有益。走进图书馆，内部空间宽敞明亮，设计感十足，尤其是那个巨大的中庭，阳光透过玻璃穹顶洒下来，光影效果非常迷人。\n\n馆内非常安静，几乎听不到一点杂音，大家都在埋头苦读。书架上摆满了各种各样的书籍，从古籍善本到最新的学术期刊应有尽有。找了一个靠窗的位置坐下，随手翻开一本书，窗外是宁静的校园景色，手边是散发着墨香的书籍，这种沉浸式阅读的感觉真的太棒了。在这里，你能真切地感受到“书山有路勤为径”的含义。羡慕在这里读书的同学们！#图书馆 #中南大学 #阅读 #建筑美学 #学习氛围",
                "comments": [
                    "这个图书馆设计真的很大气，很有现代感。",
                    "在这样的环境里学习效率一定很高吧。",
                    "羡慕别人的学校，我们学校图书馆好旧。",
                    "光影效果抓拍得很好，很有意境。",
                    "这才是大学该有的样子，沉静、博学。",
                    "想去里面坐坐，发发呆也是好的。"
                ]
            },
            {
                "image": "changsha_dufujiangge.jpg",
                "title": "夜游杜甫江阁：湘江之畔的璀璨明珠",
                "text": "“夜醉长沙酒，晓行湘水春。” 晚上的长沙，最耀眼的地标之一莫过于杜甫江阁了。这座为纪念诗圣杜甫而建的仿古建筑，在夜幕降临后，通体金碧辉煌，倒映在波光粼粼的湘江之中，美得令人窒息。\n\n我们特意选在晚上过来，吹着江风，沿着湘江风光带慢慢散步。远处的橘子洲大桥车水马龙，对岸的岳麓山轮廓隐约可见。登上江阁，视野瞬间开阔，整个长沙的江景尽收眼底。如果是周六晚上，这里还是观看橘子洲烟花的最佳位置，可惜今天没有烟花，但光是这辉煌的夜景就已经足够震撼了。江阁下还有很多市民在唱歌、跳舞，充满了生活气息。#杜甫江阁 #湘江夜景 #长沙地标 #夜游 #古建筑",
                "comments": [
                    "晚上的杜甫江阁真的太惊艳了！",
                    "金碧辉煌的，拍照都不用修图。",
                    "在这里看烟花绝对是C位，可惜现在烟花少了。",
                    "江边的风吹着很舒服，适合散步。",
                    "感觉长沙的夜景不输给一线城市啊。",
                    "杜甫如果穿越回来，看到这阁楼应该也会很欣慰吧。"
                ]
            },
            {
                "image": "changsha_huangxinglu_street.jpg",
                "title": "热闹非凡：沉浸在黄兴路步行街的人潮中",
                "text": "来到长沙，如果不来黄兴路步行街挤一挤，那绝对是不完整的！这里是长沙最繁华、最热闹的商业中心，也是感受这座城市“娱乐之都”魅力的最佳窗口。刚一踏入步行街，就被那汹涌的人潮和震耳欲聋的音乐声包围了。\n\n街道两旁商铺林立，巨大的霓虹灯招牌闪烁着诱人的光芒。当然，最吸引人的还是那无处不在的美食！臭豆腐、糖油粑粑、大香肠、茶颜悦色……每走几步就是一个排着长队的网红店。空气中弥漫着各种食物的香气，让人忍不住食指大动。虽然人真的超级多，有时候甚至要侧身才能通过，但这种热气腾腾、充满活力的市井气息，正是长沙最迷人的地方。累了就找个路边摊坐下，看着来来往往的帅哥美女，也是一种享受。#长沙美食 #步行街 #黄兴路 #逛吃逛吃 #人山人海",
                "comments": [
                    "看着就热闹，长沙人民太热情了。",
                    "茶颜悦色排队排到了吗？好想喝！",
                    "臭豆腐必须吃黑色的，闻着臭吃着香。",
                    "每次去步行街都要胖三斤回来。",
                    "虽然人多，但是气氛真的好，很有活力。",
                    "那个大香肠看着也太诱人了。"
                ]
            },
            {
                "image": "changsha_hunan_university_at_autumn.jpg",
                "title": "湖南大学的秋天：没有围墙的千年学府",
                "text": "湖南大学，这所坐落在岳麓山下、湘江之滨的“千年学府”，有着一种独特的气质。它没有围墙，完全融入了城市和自然之中。秋天的湖大，更是美得不可方物。\n\n校园里的梧桐树叶黄了，铺满了道路，踩上去沙沙作响。红砖老建筑在秋日的暖阳下显得更加庄重典雅。最著名的东方红广场上，毛主席雕像依然屹立，背后的岳麓书院更是承载了厚重的历史文化。走在校园里，既能感受到浓厚的学术氛围，又能享受到大自然的馈赠。我们还在登高路的小吃街吃了很多好吃的，帅哥烧饼果然名不虚传！在这里读书的幸福感一定很高吧，每天都能在风景区里上课。#湖南大学 #秋天 #最美校园 #岳麓山下 #人文气息",
                "comments": [
                    "开放式校园真的很少见，很有特色。",
                    "秋天的梧桐大道太有感觉了，适合拍日系照片。",
                    "帅哥烧饼还在吗？好多年的回忆了。",
                    "湖大的建筑很有历史感，中西合璧。",
                    "在这里上学真的就像住在景区里一样。",
                    "惟楚有材，于斯为盛，湖大底蕴深厚。"
                ]
            },
            {
                "image": "changsha_juzizhou.jpg",
                "title": "橘子洲头：独立寒秋，湘江北去",
                "text": "“独立寒秋，湘江北去，橘子洲头。” 哪怕不会背诗的人，到了长沙也一定要来橘子洲头打个卡。这里不仅仅是一个公园，更是一种情怀的象征。我们选择了坐小火车游览，复古的小火车穿梭在绿树丛中，别有一番风味。\n\n当巨大的毛泽东青年艺术雕像出现在眼前时，那种震撼感是无法用语言形容的。雕像目光深邃，凝视着远方，眉宇间透露出指点江山的豪迈气概。站在洲头，看着湘江水滚滚北去，两岸的高楼大厦拔地而起，古老与现代在这里完美交融。江风很大，吹得人衣角翻飞，但也让人感到心胸开阔。建议大家下午晚一点来，可以顺便看个日落，夕阳下的橘子洲更是美不胜收。#橘子洲 #伟人雕像 #长沙必打卡 #湘江 #红色旅游",
                "comments": [
                    "雕像真的很震撼，眼神非常有神。",
                    "小火车是粉红色的吗？很可爱。",
                    "我去的时候下雨了，别有一番烟雨濛濛的感觉。",
                    "指点江山，激扬文字，太有气势了。",
                    "橘子洲真的很长，走路要走断腿，必须坐车。",
                    "日落时分的橘子洲确实最美。"
                ]
            },
            {
                "image": "changsha_wuyi_square.jpg",
                "title": "五一广场的日与夜：长沙的心脏跳动",
                "text": "如果说长沙是一座不夜城，那么五一广场就是它永不停歇的心脏。无论是白天还是黑夜，这里永远车水马龙，人声鼎沸。站在天桥上俯瞰，四面八方的车流汇聚于此，周围高楼林立，巨大的LED屏幕播放着时尚的广告，现代都市的繁华感扑面而来。\n\n这里是长沙交通的枢纽，也是购物和美食的天堂。地下迷宫般的商业街，地上高端的商场，无论你是想买奢侈品还是淘小玩意，这里都能满足你。最让我印象深刻的是这里的夜生活，凌晨两三点依然灯火通明，街上全是出来觅食和游玩的年轻人。在五一广场，你永远不会感到孤独，因为这里总有人陪你一起醒着。这种旺盛的生命力，大概就是长沙最吸引人的地方吧。#五一广场 #长沙中心 #都市繁华 #不夜城 #街拍",
                "comments": [
                    "长沙人都不睡觉的吗？凌晨还这么多人。",
                    "五一广场真的是宇宙中心，太繁华了。",
                    "那个大屏幕很适合拍照打卡。",
                    "每次去五一广场都迷路，地下太复杂了。",
                    "充满活力的城市，很适合年轻人。",
                    "这里好吃的也多，就在那个7up里面。"
                ]
            },
            {
                "image": "changsha_wuyisquare2.jpg",
                "title": "繁华五一商圈：IFS国金中心打卡",
                "text": "来到五一商圈，怎么能不来最高的IFS国金中心打个卡呢？这座双子塔建筑已经成为了长沙的新地标。坐电梯直达7楼的雕塑花园，终于见到了传说中的KAWS雕塑！两个巨大的玩偶背靠背坐着，眺望着远方，造型非常独特可爱。\n\n虽然排队合影的人很多，但大家都很守秩序。站在7楼的露台上，视野极佳，可以俯瞰整个五一广场和繁华的长沙街景。IFS里面的品牌也非常齐全，各种大牌云集，逛起来非常爽。商场的设计很有艺术感，冷气也很足（夏天这点很重要！）。逛累了就在楼上找家餐厅吃饭，看着窗外的风景，非常惬意。如果你喜欢时尚和艺术，IFS绝对不容错过。#IFS #国金中心 #KAWS #长沙地标 #时尚购物",
                "comments": [
                    "KAWS真的好火，每次去都要排队。",
                    "在上面俯瞰长沙的感觉真好。",
                    "IFS里面冷气确实很足，避暑圣地。",
                    "那个雕塑很可爱，我也合影了。",
                    "长沙现在的国际化程度越来越高了。",
                    "楼上有家泰国菜很好吃，推荐。"
                ]
            },
            {
                "image": "changsha_yuelu_academy.jpg",
                "title": "千年学府岳麓书院：惟楚有材，于斯为盛",
                "text": "走进岳麓书院，仿佛穿越了时空的隧道，回到了那个书声琅琅的古代。作为中国古代四大书院之一，这里的一砖一瓦都透着浓浓的书卷气。大门口那副著名的对联“惟楚有材，于斯为盛”，更是让人感受到湖湘文化的底气与自信。\n\n书院内的建筑布局严谨，庭院深深，古树参天。讲堂、御书楼、文庙……每一处都值得细细品味。虽然现在已经是著名的旅游景点，但依然能感受到那份沉静治学的氛围。后花园的景色也非常美，亭台楼阁，小桥流水，很有江南园林的韵味。在这里慢慢走，慢慢看，了解一下朱熹、张栻等理学大师在此讲学的故事，不仅是一次视觉的享受，更是一次精神的洗礼。#岳麓书院 #文化之旅 #历史古迹 #国学 #静心",
                "comments": [
                    "惟楚有材，于斯为盛，这口气真霸气！",
                    "书院的环境真好，适合读书做学问。",
                    "在这里能感受到中国传统文化的魅力。",
                    "门票不便宜，但是值回票价。",
                    "后花园真的很漂亮，很清幽。",
                    "朱张会讲的地方，历史意义重大。"
                ]
            },
            
            # Dunhuang
            {
                "image": "dunhuang_mogaoku.jpg",
                "title": "莫高窟：穿越千年的沙漠艺术宝库",
                "text": "终于来到了心心念念的莫高窟！当看到那标志性的九层楼静静地伫立在鸣沙山断崖上时，内心的激动无法言表。这里是世界上现存规模最大、内容最丰富的佛教艺术地，是人类文明的瑰宝。\n\n在讲解员的带领下，我们参观了几个经典的洞窟。走进洞窟的那一刻，仿佛进入了一个神佛的世界。四壁和窟顶布满了精美的壁画，佛像庄严慈悲。虽然历经千年的风沙侵蚀，但那些色彩依然鲜艳，线条依然流畅。每一个洞窟都像是一个博物馆，讲述着不同的故事。特别推荐先看数字电影，非常震撼，能让你对莫高窟的历史背景有更深的了解。保护文物，人人有责，洞窟内严禁拍照，所以只能把这份美丽深深印在脑海里。#敦煌 #莫高窟 #世界文化遗产 #佛教艺术 #心灵之旅",
                "comments": [
                    "一定要看数字电影！太震撼了！",
                    "不能拍照是对的，闪光灯会破坏壁画。",
                    "九层楼真的很壮观，沙漠里的奇迹。",
                    "听讲解员说壁画的故事，感觉像穿越了一样。",
                    "票很难抢，一定要提前预约！",
                    "看到那些被破坏的壁画好心痛，一定要保护好。"
                ]
            },
            {
                "image": "dunhuang_mural1.jpg",
                "title": "敦煌壁画之美（一）：飞天曼妙，一眼千年",
                "text": "敦煌壁画最著名的莫过于飞天了。在莫高窟的壁画中，飞天不是长着翅膀的天使，而是凭借着飘曳的衣裙和飞舞的彩带，凌空翱翔。她们姿态各异，有的手持乐器，有的手捧鲜花，有的倒悬身姿，有的回首顾盼，充满了动感和生命力。\n\n看着这些壁画，你会被古人的想象力和艺术造诣所折服。他们用流畅的线条和丰富的色彩，描绘出了一个极乐世界。即使经过了千年的岁月，飞天的衣带仿佛还在风中飘动，那种轻盈、自由的感觉表现得淋漓尽致。这种美是跨越时空的，直击心灵。#敦煌飞天 #壁画艺术 #中国美学 #传统文化 #惊艳",
                "comments": [
                    "飞天的姿态真的太美了，飘逸灵动。",
                    "古人的审美真的高级，色彩搭配绝了。",
                    "这就是东方的艺术魅力啊。",
                    "感觉她们真的在天上飞一样。",
                    "反弹琵琶那个最经典，百看不厌。",
                    "好想拥有一套飞天的汉服写真。"
                ]
            },
            {
                "image": "dunhuang_mural2.jpg",
                "title": "敦煌壁画之美（二）：经变画中的佛国世界",
                "text": "除了飞天，莫高窟还有大量的经变画，也就是把深奥的佛经故事用绘画的形式表现出来。这些画作场面宏大，人物众多，细节丰富得惊人。比如著名的《西方净土变》，描绘了楼台亭阁、宝池莲花、歌舞升平的极乐世界景象。\n\n仔细看这些壁画，你会发现里面不仅有神佛，还有很多反映当时社会生活的场景，比如耕作、狩猎、婚嫁、奏乐等。这简直就是一部墙上的百科全书！画工们不仅技艺高超，而且倾注了极大的虔诚。每一笔每一划都一丝不苟，色彩的晕染也非常讲究。站在这些巨幅壁画前，你会感到自己的渺小，也会被那种宏大的叙事感所震撼。#经变画 #佛经故事 #艺术细节 #历史画卷 #匠心",
                "comments": [
                    "细节控表示一本满足，可以看一天。",
                    "原来壁画里还有这么多世俗生活的场景。",
                    "这简直就是古代的连环画嘛。",
                    "那个颜色是怎么做到千年不褪色的？太神奇了。",
                    "宏大的场面，精微的细节，叹为观止。",
                    "看完对佛教故事有了更直观的了解。"
                ]
            },
            {
                "image": "dunhuang_mural3.jpg",
                "title": "敦煌壁画之美（三）：岁月留痕，守护文明",
                "text": "在欣赏壁画美丽的同时，也能看到岁月的无情。有些壁画已经剥落，有些颜色已经氧化变黑，还有些被人为破坏的痕迹。看着这些残缺的美，心中不禁涌起一阵酸楚和惋惜。\n\n正是因为脆弱，所以才更显珍贵。一代代敦煌守护人，在在这大漠戈壁中，付出了青春和心血，只为留住这人类的瑰宝。现在的数字化保护工程做得很好，希望能让这些艺术永存。作为游客，我们能做的就是遵守规定，不触摸、不拍照，用眼睛去记录，用心灵去感受。希望千年之后，后人依然能看到这璀璨的文明之光。#文物保护 #敦煌守护人 #岁月沧桑 #文明传承 #珍惜",
                "comments": [
                    "向樊锦诗院长等守护人致敬！",
                    "看到残缺的部分真的很心痛。",
                    "保护文物，从我做起。",
                    "数字化确实是个好办法，可以让更多人看到。",
                    "这种残缺美也有一种独特的力量。",
                    "希望这些壁画能永远保存下去。"
                ]
            },

            # Hong Kong
            {
                "image": "hongkong_food.jpg",
                "title": "香港美食探店：舌尖上的港味",
                "text": "来香港，最重要的任务当然是吃！香港简直就是美食的天堂，从米其林餐厅到街头大排档，每一种味道都让人欲罢不能。今天打卡了一家老字号茶餐厅，那种复古的装修风格，瞬间让人想起了TVB的电视剧。\n\n点了一份经典的菠萝油，外皮酥脆掉渣，里面夹着冰凉的黄油，一口下去，冰火两重天，太满足了！还有丝袜奶茶，茶味浓郁，口感顺滑，不愧是正宗港味。中午去吃了烧鹅，皮脆肉嫩，油脂在嘴里爆开的感觉太爽了。晚上还准备去扫荡街头小吃，咖喱鱼蛋、鸡蛋仔、煎酿三宝……感觉带两个胃都不够用！大家来香港一定要做好胖三斤的准备哦！#香港美食 #茶餐厅 #菠萝油 #烧鹅 #吃货日记",
                "comments": [
                    "看着就好吃，口水流下来了。",
                    "丝袜奶茶是我的最爱，每天都要喝。",
                    "哪家茶餐厅呀？求推荐！",
                    "香港的烧鹅真的是一绝，别的地方吃不到。",
                    "羡慕，我也想去香港吃吃吃。",
                    "记得去吃九记牛腩，虽然排队久但是值得。"
                ]
            },
            {
                "image": "hongkong_peak_tram.jpg",
                "title": "坐山顶缆车上太平山：倾斜45度的奇妙体验",
                "text": "去太平山顶看夜景，最经典的交通方式当然是坐山顶缆车啦！这可是有着一百多年历史的交通工具。红色的复古车厢非常有英伦范儿，在站台拍照很出片。\n\n缆车启动后，最神奇的事情发生了。随着坡度越来越陡，最大甚至达到了27度，你会感觉窗外的高楼大厦都倾斜了，仿佛都要倒向自己，这种视觉错觉真的非常奇妙有趣。大概几分钟就到了山顶，虽然排队的人很多，但是这个体验绝对值得。建议大家坐右边的位置，视野会更好一些。到达山顶凌霄阁后，就可以俯瞰整个维多利亚港了，期待今晚的夜景！#太平山顶 #山顶缆车 #香港旅游 #奇妙体验 #复古交通",
                "comments": [
                    "坐这个缆车真的会感觉楼是歪的，很神奇。",
                    "红色的缆车很好看，很有电影感。",
                    "排队排了多久？听说周末人超级多。",
                    "坐右边确实风景更好，记住了。",
                    "一百多年历史了，还在运行，真厉害。",
                    "上去之后一定要去摩天台，风景无敌。"
                ]
            },
            {
                "image": "hongkong_the_buddist.jpg",
                "title": "大屿山天坛大佛：洗涤心灵的朝圣之旅",
                "text": "如果你厌倦了市区的喧嚣，不妨来大屿山走走。坐昂坪360缆车水晶车厢过来，脚下就是大海和山林，风景绝美。下了缆车，远远就能看到那尊巨大的天坛大佛端坐在山顶，庄严肃穆。\n\n要近距离瞻仰大佛，需要爬上268级台阶。虽然听起来有点累，但是一步一步走上去的过程，也是一种修行的体验。当你气喘吁吁地站在大佛脚下，抬头仰望那慈悲的面容，内心会感到无比的平静和震撼。大佛周围群山环抱，云雾缭绕，真的很有灵气。参观完大佛，还可以去旁边的宝莲禅寺吃一顿斋饭，味道清淡可口。这一趟旅程，感觉身心都得到了净化。#大屿山 #天坛大佛 #昂坪360 #心灵净化 #佛教圣地",
                "comments": [
                    "爬上去确实累，但是上面的风景很值得。",
                    "水晶缆车敢坐吗？我是有点恐高。",
                    "大佛真的很宏伟，很有气势。",
                    "宝莲寺的斋饭确实不错，推荐。",
                    "那里空气很好，很适合放松心情。",
                    "一种远离尘世的感觉，很宁静。"
                ]
            },
            {
                "image": "hongkong_victoria_harbour_view_from_icc_sky100.jpg",
                "title": "天际100俯瞰维港：上帝视角的香港",
                "text": "想要360度无死角地欣赏香港的美景，天际100观景台绝对是最佳选择。它位于全港最高的环球贸易广场（ICC）的100楼，坐电梯只需要60秒就能到达，速度快到耳膜都有点鼓胀感。\n\n站在393米的高空，透过巨大的落地玻璃窗，整个维多利亚港和九龙半岛的景色尽收眼底。白天的维港繁忙而充满活力，船只穿梭；傍晚时分看日落更是绝美，金色的余晖洒满海面，城市慢慢亮起灯火。我们特意等到晚上，看着脚下的摩天大楼变成了璀璨的星河，那种繁华与壮观真的让人震撼。这里还有很多互动设施和拍照打卡点，非常适合情侣或者带小朋友来。#天际100 #香港最高 #上帝视角 #维多利亚港 #城市天际线",
                "comments": [
                    "在这个高度看香港，感觉真的很不一样。",
                    "恐高症患者表示腿软，但是又想看。",
                    "夜景真的太绝了，不愧是东方之珠。",
                    "电梯真的超级快，嗖的一下就到了。",
                    "票价虽然有点贵，但是风景值了。",
                    "在这里看日落简直是人生享受。"
                ]
            },

            # Shanghai
            {
                "image": "shanghai_chenghuangmiao_temple.jpg",
                "title": "城隍庙的古韵：繁华都市里的传统记忆",
                "text": "在上海这样一座现代化大都市里，城隍庙是一个独特的存在。走进这里，仿佛穿越回了明清时期的江南。飞檐翘角，雕梁画栋，红墙黛瓦，每一处建筑都透着浓浓的古韵。\n\n最著名的九曲桥上总是人山人海，据说走过九曲桥可以曲折通幽，驱邪避灾。桥下的池塘里锦鲤成群，荷花盛开时更是美不胜收。虽然这里商业气息比较浓，但是那种热闹的民俗氛围还是很吸引人。各种老字号云集，南翔小笼包、五香豆、梨膏糖……排队的人络绎不绝。在这里，你可以一边品尝地道的小吃，一边欣赏传统的建筑，感受上海老城厢的独特魅力。#上海城隍庙 #豫园 #古建筑 #民俗文化 #老上海",
                "comments": [
                    "九曲桥上人真的太多了，挤不动。",
                    "南翔小笼包一定要去吃，皮薄馅大。",
                    "虽然是游客打卡地，但是建筑真的很美。",
                    "过年的时候有灯会，那时候最漂亮。",
                    "在这里买点特产送人挺不错的。",
                    "很有中国味的地方，老外特别多。"
                ]
            },
            {
                "image": "shanghai_chenghunagmiao_temple2.avif",
                "title": "夜色下的城隍庙：流光溢彩的梦幻世界",
                "text": "如果说白天的城隍庙是古朴喧闹的，那么晚上的城隍庙则是金碧辉煌、流光溢彩的。当夜幕降临，所有的建筑都亮起了金色的灯光，轮廓被勾勒得清晰可见，倒映在水中，美得像是一个梦幻的宫殿。\n\n我们在晚上又特意来逛了一圈，感觉比白天更有韵味。灯光下的古建筑少了白天的喧嚣，多了一份神秘和华丽。走在灯火通明的街道上，看着熙熙攘攘的人群，仿佛置身于古代的上元灯会。特别推荐晚上来九曲桥拍照，背景是发光的湖心亭，随便拍都是大片。如果你来上海，一定要留一个晚上给城隍庙，绝对不会让你失望。#夜游上海 #城隍庙夜景 #金碧辉煌 #梦回大唐 #摄影打卡",
                "comments": [
                    "晚上的灯光确实很漂亮，富丽堂皇。",
                    "感觉比白天好看多了，白天人太多太杂。",
                    "拍出来的照片很有质感，像古装剧场景。",
                    "真的很像千与千寻里的场景。",
                    "晚上去吃个夜宵，逛逛灯会，美滋滋。",
                    "这才是魔都该有的夜景。"
                ]
            },
            {
                "image": "shanghai_disney_land.jpg",
                "title": "上海迪士尼：点亮心中奇梦的一天",
                "text": "全世界都在催着你长大，只有迪士尼在守护你的童心。今天终于来到了上海迪士尼乐园，开启了一场神奇的童话之旅！一进园就被那种快乐的氛围感染了，每个人脸上都洋溢着笑容，戴着可爱的发箍。\n\n一定要去玩“创极速光轮”，那种未来感和速度感简直太刺激了！还有“飞越地平线”，带着你环游世界，视觉效果满分。花车巡游也是重头戏，看到米奇、尼克、朱迪这些熟悉的卡通人物向你招手，真的会忍不住跟着一起欢呼。当然，最最不能错过的就是晚上的烟花秀！当城堡被灯光点亮，烟花在夜空中绽放，经典的音乐响起那一刻，眼泪真的会忍不住掉下来。那一刻，真的相信魔法是存在的。#上海迪士尼 #童话世界 #烟花秀 #快乐源泉 #在逃公主",
                "comments": [
                    "烟花秀真的是看一次哭一次，太感动了。",
                    "创极速光轮yyds！一定要玩！",
                    "我也想去当在逃公主。",
                    "人多吗？排队是不是要排很久？",
                    "玲娜贝儿太可爱了，女明星！",
                    "无论几岁，去迪士尼都会变回孩子。"
                ]
            },
            {
                "image": "shanghai_food.jpg",
                "title": "地道上海本帮菜：浓油赤酱的诱惑",
                "text": "来到上海，怎么能不尝尝地道的本帮菜呢？上海菜的特点就是“浓油赤酱，咸淡适中，保持原味，醇厚鲜美”。今天去了一家本地人推荐的老馆子，味道真的很正宗。\n\n必点的红烧肉，色泽红亮，肥而不腻，入口即化，带着上海菜特有的甜味，简直是下饭神器！还有响油鳝丝，端上来的时候还在滋滋作响，胡椒粉的味道恰到好处，鲜美无比。草头圈子也是一绝，肥肠处理得很干净，配上清爽的草头，口感丰富。虽然有人可能觉得上海菜偏甜，但我个人非常喜欢这种鲜甜的口感，让人回味无穷。吃完这一顿，感觉对上海这座城市的爱又多了一分。#上海美食 #本帮菜 #红烧肉 #浓油赤酱 #吃货探店",
                "comments": [
                    "红烧肉看着太诱人了，想吃！",
                    "上海菜确实偏甜，但是好吃的。",
                    "响油鳝丝也是我的最爱，鲜得掉眉毛。",
                    "求店铺名字！下次去上海也要去吃。",
                    "草头圈子绝了，肥肠爱好者的福音。",
                    "看饿了，这大晚上的放毒。"
                ]
            },
            {
                "image": "shanghai_lujiazui_at_sunrise.jpg",
                "title": "陆家嘴的日出：见证城市的苏醒",
                "text": "为了看这场日出，我们凌晨四点就起床了，来到了外滩的观景平台。清晨的上海，褪去了白天的喧嚣，显得格外宁静。江风微凉，吹得人很清醒。\n\n慢慢地，东方的天空开始泛起鱼肚白，接着变成了粉色、金色。当太阳从陆家嘴的摩天大楼背后缓缓升起时，整个画面太震撼了！金色的阳光洒在上海中心、环球金融中心和金茂大厦的玻璃幕墙上，折射出耀眼的光芒。黄浦江的水面也被染成了金色，波光粼粼。这一刻，我感受到了这座国际大都市蓬勃的生命力。早起虽然痛苦，但是看到这样的美景，一切都值了！如果你也是摄影爱好者，一定不要错过陆家嘴的日出。#陆家嘴 #日出 #外滩 #魔都晨光 #摄影大片",
                "comments": [
                    "太美了，这个色调真的绝。",
                    "佩服博主起这么早，我起不来。",
                    "早晨的外滩确实别有一番风味。",
                    "城市的苏醒，充满希望的感觉。",
                    "这照片可以拿去做壁纸了。",
                    "下次我也要去蹲个日出。"
                ]
            },
            {
                "image": "shanghai_lujiazui_night_view_3.webp",
                "title": "魔都璀璨夜景：外滩视角的视觉盛宴",
                "text": "“夜上海，夜上海，你是个不夜城……” 只有站在外滩，看着对岸陆家嘴的夜景，你才能真正理解这句话的含义。这里是上海最经典、最迷人的名片。\n\n隔着黄浦江，对岸的“陆家嘴三件套”——上海中心、环球金融中心、金茂大厦，高耸入云，灯火通明。东方明珠塔闪烁着彩色的光芒，像一颗巨大的宝石镶嵌在夜空中。江面上游船穿梭，流光溢彩。背后的万国建筑博览群也亮起了金色的灯光，复古而庄重。古典与现代，历史与未来，在这里隔江相望，完美融合。站在江边，吹着晚风，看着这繁华盛世，真的会让人沉醉其中，流连忘返。#魔都夜景 #外滩 #陆家嘴 #东方明珠 #繁华",
                "comments": [
                    "这夜景，真的是国内天花板了。",
                    "每次去上海都要去外滩吹吹风。",
                    "虽然人多，但是风景真的无敌。",
                    "东方明珠塔真的是从小看到大，依然觉得美。",
                    "这种繁华感，只有上海能给。",
                    "拍得真好，把魔都的气质拍出来了。"
                ]
            },
            {
                "image": "shanghai_lujiazui_nightview.jpg",
                "title": "不夜城上海：深入陆家嘴的钢铁森林",
                "text": "在外滩看是远观，走进陆家嘴则是身临其境的震撼。当你站在这些几百米高的摩天大楼脚下抬头仰望时，会感到一种强烈的压迫感和未来感，仿佛置身于科幻电影的场景中。\n\n夜晚的陆家嘴，街道宽阔整洁，两旁的高楼灯火辉煌。走在世纪天桥上，被四周的钢铁森林包围，上海中心大厦直插云霄，顶部的灯光在云雾中若隐若现。这里聚集了全世界的金融精英，每一盏灯光背后可能都在进行着亿万级的交易。这里的节奏很快，空气中都弥漫着金钱和梦想的味道。在这里拍照真的非常赛博朋克，随便一拍都是大片。#陆家嘴 #摩天大楼 #赛博朋克 #金融中心 #魔都",
                "comments": [
                    "那个大圆环天桥是必打卡点。",
                    "治好了我的颈椎病，一直在抬头看。",
                    "这里真的很有未来感，像电影一样。",
                    "身临其境的感觉确实很压迫，人类好渺小。",
                    "晚上的陆家嘴比白天好看太多了。",
                    "在这里上班的人应该压力很大吧。"
                ]
            },
            {
                "image": "shanghai_lujiazui_nightview2.jpg",
                "title": "金融中心的夜：云端之上的视角",
                "text": "今晚我们登上了上海中心大厦的“上海之巅”观光厅，站在118层、546米的高空俯瞰上海。这是一种完全不同的体验，感觉整个城市都在你的脚下。\n\n透过360度的落地窗，可以看到金茂大厦和环球金融中心都在我们下方，平时高不可攀的摩天大楼此刻都变成了积木。黄浦江像一条发光的丝带蜿蜒穿过城市，外滩的建筑群像是一个个精致的模型。远处的灯火一直延伸到地平线，仿佛没有尽头。站在这里，你会感叹人类的伟大，也能感受到上海这座城市的无限可能。虽然票价不便宜，但是这种“会当凌绝顶”的感觉，绝对是人生难得的体验。#上海中心 #上海之巅 #高空观景 #俯瞰魔都 #震撼",
                "comments": [
                    "在云端的感觉，太酷了！",
                    "上海中心是最高的，俯视一切。",
                    "看着下面的车流像蚂蚁一样。",
                    "晚上去玻璃反光严重吗？好想去拍。",
                    "恐高的人估计腿都要软了。",
                    "这才是真正的上帝视角。"
                ]
            },
            {
                "image": "shanghai_nanjinglu_street.jpg",
                "title": "南京路步行街：中华商业第一街的魅力",
                "text": "“十里南京路，一个新上海。” 南京路步行街是上海开埠后最早建立的一条商业街，也是无数游客来上海的必经之地。这里既有永安百货、先施公司等百年老字号，也有各种现代化的时尚商场。\n\n走在步行街上，最吸睛的莫过于那辆复古的“铛铛车”，坐在车上看着两旁的建筑和熙熙攘攘的人群，别有一番风味。街道两旁的霓虹灯招牌密密麻麻，非常有老上海的味道。我们逛了逛沈大成、泰康食品，买了些鲜肉月饼和蝴蝶酥，味道真的很赞！虽然这里商业化程度很高，人也超级多，但是那种热闹繁华的氛围，依然让人忍不住想融入其中。#南京路步行街 #中华第一街 #老字号 #上海购物 #铛铛车",
                "comments": [
                    "铛铛车一定要坐，很有感觉。",
                    "沈大成的青团和条头糕很好吃！",
                    "鲜肉月饼刚出炉的简直是人间美味。",
                    "南京路的霓虹灯招牌很有赛博朋克感。",
                    "人真的太多了，走路都要排队。",
                    "每次去都要买一大堆特产回家。"
                ]
            },
            {
                "image": "shanghai_the_bund.jpg",
                "title": "万国建筑博览群：阅读外滩的石头史书",
                "text": "外滩的精华，在于那52幢风格迥异的古典复兴大楼，被誉为“万国建筑博览群”。这些建筑历经百年风雨，依然保存完好，每一块石头都刻录着上海的历史沧桑。\n\n沿着中山东一路漫步，你可以看到哥特式的尖顶、古希腊式的穹隆、巴洛克式的廊柱……海关大楼的钟声依然按时敲响，浑厚的声音回荡在浦江上空。和平饭店的绿色屋顶在阳光下格外醒目，诉说着旧上海的传奇故事。建议大家不仅要看夜景，白天也要来看看这些建筑的细节，感受那种厚重的历史底蕴。这里是上海的起点，也是读懂上海的最佳去处。#外滩建筑群 #历史建筑 #海关大楼 #和平饭店 #上海记忆",
                "comments": [
                    "这些建筑真的很有味道，百看不厌。",
                    "海关大楼的钟声听着很让人安心。",
                    "和平饭店的老爵士乐队还在演出吗？",
                    "每一栋楼都有故事，值得细细品味。",
                    "白天看细节，晚上看灯光，都很美。",
                    "这才是上海的底蕴所在。"
                ]
            },

            # Zhangjiajie
            {
                "image": "zhangjiajie_avatar_mountains.jpg",
                "title": "阿凡达悬浮山原型：走进潘多拉星球",
                "text": "当你亲眼看到张家界的乾坤柱时，你就会明白为什么《阿凡达》会选这里作为悬浮山的原型了。那种视觉冲击力真的太强了！一根根石柱拔地而起，直插云霄，下临深渊，造型奇特。\n\n今天运气特别好，山间刚好有云雾缭绕。那些石柱在云雾中若隐若现，真的就像是悬浮在空中一样，神秘莫测。站在观景台上，仿佛自己真的置身于潘多拉星球，随时会有纳威人骑着飞龙出现。大自然的鬼斧神工真的让人惊叹不已，数亿年的地质演变才造就了这独一无二的地貌。这里绝对是一生必去的地方之一！#张家界 #阿凡达 #哈利路亚山 #乾坤柱 #自然奇观",
                "comments": [
                    "真的好像电影里的场景啊！",
                    "云雾缭绕的时候最美，像仙境一样。",
                    "大自然真是太神奇了，鬼斧神工。",
                    "看着都有点腿软，好高啊。",
                    "一定要去现场看，照片拍不出那种震撼。",
                    "张家界的地貌确实是世界独有的。"
                ]
            },
            {
                "image": "zhangjiajie_cable_car.jpg",
                "title": "天门山索道：飞越云端的惊险之旅",
                "text": "去天门山，单程近30分钟的索道是必体验的项目。这可是世界上最长的高山客运索道，全长7455米，高差1279米！坐在缆车里，从市中心直接飞向高山之巅，这种体验绝无仅有。\n\n随着缆车缓缓上升，脚下的风景在不断变化。先是城市的屋顶，然后是田园风光，最后是险峻的山峰。特别是中段，缆车在几乎垂直的峭壁上攀升，脚下就是万丈深渊，恐高的人可能会吓得不敢睁眼，但是胆子大的人会觉得超级刺激！透过玻璃窗，还能看到著名的“通天大道”——99道弯的盘山公路，像一条巨龙盘旋在山间。这不仅是交通工具，更是一场视觉盛宴。#天门山索道 #高空挑战 #通天大道 #张家界旅游 #心跳加速",
                "comments": [
                    "这个索道真的很长，坐了好久。",
                    "看着脚下的盘山公路，真的太壮观了。",
                    "恐高症全程闭眼，手心冒汗。",
                    "穿过云层的感觉太棒了。",
                    "世界上最长的索道，名不虚传。",
                    "一定要抢个靠窗的位置拍照。"
                ]
            },
            {
                "image": "zhangjiajie_tianmenshan.jpg",
                "title": "天门洞开：攀登999级天梯的朝圣",
                "text": "天门山最标志性的景点就是天门洞了。这是一个天然形成的穿山溶洞，高悬在千米峭壁之上，南北对开，气势磅礴。远远望去，就像是通往天界的门户。\n\n要到达天门洞，必须挑战999级“上天梯”。这台阶非常陡峭，看着都让人腿软。但是既然来了，就没有退缩的理由！我们一步一步往上爬，累了就歇会儿，看看周围的风景。当你终于爬完最后一级台阶，站在天门洞下，感受着穿洞而过的山风，那种成就感油然而生。这里还经常有翼装飞行表演，看着勇士们从洞口穿越，真的太惊险了。#天门洞 #上天梯 #登山挑战 #天门山 #壮观",
                "comments": [
                    "爬完999级台阶，腿废了三天。",
                    "不想爬的可以坐穿山扶梯，很方便。",
                    "站在洞口真的很凉快，风很大。",
                    "真的是大自然的奇迹，怎么形成的呢？",
                    "寓意长长久久，情侣一定要一起爬。",
                    "翼装飞行太猛了，看着都害怕。"
                ]
            },
            {
                "image": "zhangjiajie_yuanjiajie.webp",
                "title": "袁家界奇观：天下第一桥与迷魂台",
                "text": "袁家界是张家界国家森林公园的核心景区，这里的景色以“奇、险、秀”著称。其中最让我震撼的是“天下第一桥”。这是一座天然形成的石桥，横跨在两座高耸的山峰之间，桥面宽仅两米，厚五米，跨度却有五十多米，高度近四百米！不得不感叹大自然的神奇造化。\n\n还有“迷魂台”，顾名思义，这里的景色美得让人魂迷。站在观景台上，眼前是成百上千座石峰拔地而起，形态各异，有的像人，有的像兽，错落有致。尤其是在雨后初晴，云雾在山峰间流动，如梦如幻，真的让人流连忘返，不愿离去。袁家界绝对是摄影爱好者的天堂，随便一拍都是风光大片。#袁家界 #天下第一桥 #迷魂台 #张家界核心 #绝美风光",
                "comments": [
                    "天下第一桥真的很险，佩服大自然。",
                    "迷魂台名字起得好，真的会被迷住。",
                    "百龙天梯也很壮观，直接上袁家界。",
                    "这里的猴子很多，要小心手里的食物。",
                    "张家界的山真的是看不够，太独特了。",
                    "除了人多，没有缺点。"
                ]
            }
        ]

        posts = []
        user_index = 0
        
        for post_data in destinations:
            # Assign a user cyclically
            author = users[user_index % len(users)]
            user_index += 1
            
            post = PostPO(
                id=generate_uuid(),
                author_id=author.id,
                title=post_data["title"],
                text=post_data["text"],
                visibility=PostVisibility.PUBLIC.value,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 60))
            )
            session.add(post)
            posts.append(post)
            
            # Add Image
            img_url = f"/static/uploads/post_images/{post_data['image']}"
            post_img = PostImagePO(
                post_id=post.id,
                image_url=img_url,
                display_order=0
            )
            session.add(post_img)
            
            # Update JSON fields for consistency
            post.images_json = json.dumps([img_url])
            
            # Add Tags (Simple extraction from text)
            tag_list = []
            if "#" in post_data["text"]:
                tags = [t.strip() for t in post_data["text"].split("#") if t.strip()]
                # First part is text, subsequent are tags
                for tag_text in tags[1:]: 
                    # Clean up tag text (take first word)
                    tag_clean = tag_text.split()[0]
                    tag = PostTagPO(post_id=post.id, tag=tag_clean)
                    session.add(tag)
                    tag_list.append(tag_clean)
            
            post.tags_json = json.dumps(tag_list)

            # Add Specific Comments
            specific_comments = post_data.get("comments", [])
            # Randomly select 3-6 comments for each post
            num_comments = random.randint(3, len(specific_comments))
            selected_comments = random.sample(specific_comments, num_comments)
            
            # Select commenters (ensure diversity)
            commenters = []
            while len(commenters) < num_comments:
                commenters.extend(users)
            random.shuffle(commenters)
            
            for i, comment_content in enumerate(selected_comments):
                commenter = commenters[i]
                comment = CommentPO(
                    id=generate_uuid(),
                    post_id=post.id,
                    author_id=commenter.id,
                    content=comment_content,
                    created_at=post.created_at + timedelta(minutes=random.randint(10, 1000))
                )
                session.add(comment)

        session.commit()
        print(f"Created {len(posts)} posts with specific comments.")

        # 5. Add Likes (Keep generic logic for likes)
        print("Adding likes...")
        for post in posts:
            # Random likes
            num_likes = random.randint(0, len(users))
            likers = random.sample(users, num_likes)
            for liker in likers:
                like = LikePO(user_id=liker.id, post_id=post.id)
                session.add(like)
        
        session.commit()

        # 6. Create Trips
        print("Creating trips...")
        
        trips_data = [
            {
                "name": "穿越古今北京城",
                "description": "五天深度游北京，感受皇城威严与胡同烟火气。探寻历史足迹，品尝地道京味美食。",
                "cover": "beijing_the_forbidden_city.jpg",
                "days": 5,
                "budget": 6000,
                "start_delay": 10,
                "activities": [
                    [ # Day 1
                        {"name": "抵达北京", "type": "transport", "loc": "北京市顺义区首都国际机场", "start": (10, 0), "end": (12, 0)},
                        {"name": "入住酒店", "type": "accommodation", "loc": "北京市东城区王府井大街", "start": (13, 0), "end": (14, 0)},
                        {"name": "逛王府井步行街", "type": "sightseeing", "loc": "北京市东城区王府井步行街", "start": (15, 0), "end": (18, 0)},
                        {"name": "全聚德烤鸭", "type": "dining", "loc": "北京市东城区前门大街全聚德", "start": (18, 30), "end": (20, 0)}
                    ],
                    [ # Day 2
                        {"name": "天安门升旗", "type": "sightseeing", "loc": "北京市东城区天安门广场", "start": (5, 0), "end": (7, 0)},
                        {"name": "故宫博物院", "type": "sightseeing", "loc": "北京市东城区景山前街4号", "start": (8, 30), "end": (16, 0)},
                        {"name": "景山公园看日落", "type": "sightseeing", "loc": "北京市西城区景山西街44号", "start": (16, 30), "end": (18, 0)}
                    ],
                    [ # Day 3
                        {"name": "八达岭长城", "type": "sightseeing", "loc": "北京市延庆区八达岭镇", "start": (8, 0), "end": (14, 0)},
                        {"name": "鸟巢水立方", "type": "sightseeing", "loc": "北京市朝阳区奥林匹克公园", "start": (16, 0), "end": (19, 0)}
                    ],
                    [ # Day 4
                        {"name": "颐和园", "type": "sightseeing", "loc": "北京市海淀区新建宫门路19号", "start": (9, 0), "end": (13, 0)},
                        {"name": "圆明园", "type": "sightseeing", "loc": "北京市海淀区清华西路28号", "start": (14, 0), "end": (17, 0)},
                        {"name": "南锣鼓巷", "type": "sightseeing", "loc": "北京市东城区南锣鼓巷", "start": (18, 0), "end": (21, 0)}
                    ],
                    [ # Day 5
                        {"name": "天坛公园", "type": "sightseeing", "loc": "北京市东城区天坛东里甲1号", "start": (8, 30), "end": (11, 30)},
                        {"name": "前门大街", "type": "sightseeing", "loc": "北京市东城区前门大街", "start": (12, 0), "end": (14, 0)},
                        {"name": "送机", "type": "transport", "loc": "北京市顺义区首都国际机场", "start": (15, 0), "end": (17, 0)}
                    ]
                ]
            },
            {
                "name": "热辣长沙，快乐之都",
                "description": "四天三晚吃喝玩乐在长沙。打卡网红景点，挑战变态辣，感受星城的魅力。",
                "cover": "changsha_at_dusk.jpg",
                "days": 4,
                "budget": 3000,
                "start_delay": 5,
                "activities": [
                    [ # Day 1
                        {"name": "抵达长沙", "type": "transport", "loc": "长沙市长沙县黄花国际机场", "start": (11, 0), "end": (13, 0)},
                        {"name": "五一广场逛吃", "type": "dining", "loc": "长沙市芙蓉区五一广场", "start": (14, 0), "end": (17, 0)},
                        {"name": "IFS打卡", "type": "sightseeing", "loc": "长沙市芙蓉区解放西路IFS国金中心", "start": (17, 30), "end": (19, 0)},
                        {"name": "解放西路酒吧街", "type": "entertainment", "loc": "长沙市天心区解放西路", "start": (20, 0), "end": (23, 0)}
                    ],
                    [ # Day 2
                        {"name": "岳麓山爬山", "type": "sightseeing", "loc": "长沙市岳麓区岳麓山风景名胜区", "start": (8, 30), "end": (12, 0)},
                        {"name": "爱晚亭", "type": "sightseeing", "loc": "长沙市岳麓区岳麓山爱晚亭", "start": (12, 0), "end": (13, 0)},
                        {"name": "岳麓书院", "type": "sightseeing", "loc": "长沙市岳麓区麓山路273号", "start": (14, 0), "end": (16, 0)},
                        {"name": "湖南大学美食街", "type": "dining", "loc": "长沙市岳麓区麓山南路", "start": (17, 0), "end": (19, 0)}
                    ],
                    [ # Day 3
                        {"name": "橘子洲头", "type": "sightseeing", "loc": "长沙市岳麓区橘子洲头", "start": (9, 0), "end": (12, 0)},
                        {"name": "湖南省博物馆", "type": "sightseeing", "loc": "长沙市开福区东风路50号", "start": (14, 0), "end": (17, 0)},
                        {"name": "文和友晚餐", "type": "dining", "loc": "长沙市天心区湘江中路海信广场", "start": (18, 0), "end": (20, 0)},
                        {"name": "杜甫江阁夜景", "type": "sightseeing", "loc": "长沙市天心区湘江中路二段", "start": (20, 30), "end": (22, 0)}
                    ],
                    [ # Day 4
                        {"name": "米粉街早餐", "type": "dining", "loc": "长沙市芙蓉区韭菜园北路", "start": (9, 0), "end": (10, 30)},
                        {"name": "李自健美术馆", "type": "sightseeing", "loc": "长沙市岳麓区潇湘南路385号", "start": (11, 0), "end": (14, 0)},
                        {"name": "返程", "type": "transport", "loc": "长沙市雨花区长沙南站", "start": (15, 0), "end": (16, 0)}
                    ]
                ]
            },
            {
                "name": "东方之珠漫游记",
                "description": "香港四日游，体验国际大都市的繁华与市井气息的交融。购物天堂，美食之都。",
                "cover": "hongkong_victoria_harbour_panorama_view.jpg",
                "days": 4,
                "budget": 8000,
                "start_delay": 15,
                "activities": [
                    [ # Day 1
                        {"name": "抵达香港", "type": "transport", "loc": "香港离岛区赤鱲角香港国际机场", "start": (12, 0), "end": (14, 0)},
                        {"name": "入住尖沙咀酒店", "type": "accommodation", "loc": "香港油尖旺区尖沙咀", "start": (15, 0), "end": (16, 0)},
                        {"name": "维多利亚港夜景", "type": "sightseeing", "loc": "香港油尖旺区维多利亚港", "start": (19, 0), "end": (21, 0)}
                    ],
                    [ # Day 2
                        {"name": "香港迪士尼乐园", "type": "entertainment", "loc": "香港离岛区大屿山香港迪士尼乐园", "start": (9, 0), "end": (21, 0)}
                    ],
                    [ # Day 3
                        {"name": "太平山顶", "type": "sightseeing", "loc": "香港中西区太平山顶", "start": (9, 0), "end": (12, 0)},
                        {"name": "中环半山扶梯", "type": "sightseeing", "loc": "香港中西区中环半山扶梯", "start": (13, 0), "end": (15, 0)},
                        {"name": "铜锣湾购物", "type": "shopping", "loc": "香港湾仔区铜锣湾时代广场", "start": (16, 0), "end": (20, 0)}
                    ],
                    [ # Day 4
                        {"name": "旺角街头美食", "type": "dining", "loc": "香港油尖旺区旺角西洋菜南街", "start": (10, 0), "end": (13, 0)},
                        {"name": "西九龙文化区", "type": "sightseeing", "loc": "香港油尖旺区西九龙文化区", "start": (14, 0), "end": (16, 0)},
                        {"name": "乘高铁离开", "type": "transport", "loc": "香港油尖旺区西九龙站", "start": (17, 0), "end": (18, 0)}
                    ]
                ]
            },
            {
                "name": "魔都繁华梦",
                "description": "五天玩转上海，从外滩的万国建筑到陆家嘴的摩天大楼，从老弄堂到迪士尼。",
                "cover": "shanghai_panorama_view.jpg",
                "days": 5,
                "budget": 7000,
                "start_delay": 20,
                "activities": [
                    [ # Day 1
                        {"name": "抵达上海", "type": "transport", "loc": "上海市闵行区虹桥火车站", "start": (10, 0), "end": (12, 0)},
                        {"name": "南京路步行街", "type": "sightseeing", "loc": "上海市黄浦区南京东路步行街", "start": (14, 0), "end": (17, 0)},
                        {"name": "外滩夜景", "type": "sightseeing", "loc": "上海市黄浦区外滩中山东一路", "start": (18, 0), "end": (21, 0)}
                    ],
                    [ # Day 2
                        {"name": "陆家嘴三件套", "type": "sightseeing", "loc": "上海市浦东新区陆家嘴", "start": (9, 0), "end": (12, 0)},
                        {"name": "东方明珠", "type": "sightseeing", "loc": "上海市浦东新区世纪大道1号", "start": (13, 0), "end": (16, 0)},
                        {"name": "黄浦江游船", "type": "sightseeing", "loc": "上海市黄浦区十六铺码头", "start": (19, 0), "end": (20, 30)}
                    ],
                    [ # Day 3
                        {"name": "上海迪士尼乐园", "type": "entertainment", "loc": "上海市浦东新区迪士尼度假区", "start": (8, 0), "end": (22, 0)}
                    ],
                    [ # Day 4
                        {"name": "武康路Citywalk", "type": "sightseeing", "loc": "上海市徐汇区武康路", "start": (10, 0), "end": (13, 0)},
                        {"name": "豫园城隍庙", "type": "sightseeing", "loc": "上海市黄浦区豫园老街", "start": (14, 0), "end": (17, 0)},
                        {"name": "新天地", "type": "entertainment", "loc": "上海市黄浦区新天地", "start": (19, 0), "end": (22, 0)}
                    ],
                    [ # Day 5
                        {"name": "上海博物馆", "type": "sightseeing", "loc": "上海市黄浦区人民大道201号", "start": (9, 0), "end": (12, 0)},
                        {"name": "田子坊", "type": "sightseeing", "loc": "上海市黄浦区泰康路210弄", "start": (13, 0), "end": (15, 0)},
                        {"name": "送机", "type": "transport", "loc": "上海市浦东新区浦东国际机场", "start": (16, 0), "end": (18, 0)}
                    ]
                ]
            }
        ]

        for trip_info in trips_data:
            creator = random.choice(users)
            trip = TripPO(
                id=generate_uuid(),
                name=trip_info["name"],
                description=trip_info["description"],
                creator_id=creator.id,
                start_date=date.today() + timedelta(days=trip_info["start_delay"]),
                end_date=date.today() + timedelta(days=trip_info["start_delay"] + trip_info["days"] - 1),
                visibility=TripVisibility.PUBLIC.value,
                status=TripStatus.PLANNING.value,
                budget_amount=trip_info["budget"],
                cover_image_url=f"/static/uploads/trip_covers/{trip_info['cover']}"
            )
            session.add(trip)
            session.flush() # get ID

            # Add creator as admin
            tm = TripMemberPO(trip_id=trip.id, user_id=creator.id, role=MemberRole.ADMIN.value, nickname="发起人")
            session.add(tm)
            
            # Add random members
            potential_members = [u for u in users if u.id != creator.id]
            members = random.sample(potential_members, random.randint(1, 3))
            for mem in members:
                tm_mem = TripMemberPO(trip_id=trip.id, user_id=mem.id, role=MemberRole.MEMBER.value, nickname="团员")
                session.add(tm_mem)

            # Add Days and Activities
            for day_idx, activities in enumerate(trip_info["activities"]):
                day_num = day_idx + 1
                trip_day = TripDayPO(
                    trip_id=trip.id,
                    day_number=day_num,
                    date=trip.start_date + timedelta(days=day_idx),
                    theme=f"第{day_num}天行程"
                )
                session.add(trip_day)
                session.flush()

                for act in activities:
                    activity = ActivityPO(
                        id=generate_uuid(),
                        trip_day_id=trip_day.id,
                        name=act["name"],
                        activity_type=act["type"],
                        location_name=act["loc"],
                        start_time=time(*act["start"]),
                        end_time=time(*act["end"])
                    )
                    session.add(activity)

        session.commit()
        print(f"Created {len(trips_data)} trips.")

        # 7. Create Conversations (Keep simple)
        print("Creating conversations...")
        u1 = users[0]
        u2 = users[1]
        
        conv = ConversationPO(
            id=generate_uuid(),
            conversation_type=ConversationType.PRIVATE.value,
            created_at=datetime.utcnow()
        )
        session.add(conv)
        session.flush()

        stmt = conversation_participants.insert().values([
            {'conversation_id': conv.id, 'user_id': u1.id, 'role': ConversationRole.MEMBER.value},
            {'conversation_id': conv.id, 'user_id': u2.id, 'role': ConversationRole.MEMBER.value}
        ])
        session.execute(stmt)

        msg1 = MessagePO(
            id=generate_uuid(),
            conversation_id=conv.id,
            sender_id=u1.id,
            content_text="我们去北京的旅行计划得怎么样了？",
            message_type="text",
            sent_at=datetime.utcnow()
        )
        msg2 = MessagePO(
            id=generate_uuid(),
            conversation_id=conv.id,
            sender_id=u2.id,
            content_text="我看了一下，行程安排得很满，我很期待！",
            message_type="text",
            sent_at=datetime.utcnow() + timedelta(seconds=10)
        )
        session.add(msg1)
        session.add(msg2)
        
        session.commit()
        
        print("Database initialization completed successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    init_data()
