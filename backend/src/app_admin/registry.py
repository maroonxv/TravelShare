from app_auth.infrastructure.database.persistent_model.user_po import UserPO
from app_social.infrastructure.database.persistent_model.post_po import PostPO, CommentPO, LikePO, PostImagePO, PostTagPO
from app_social.infrastructure.database.persistent_model.conversation_po import ConversationPO
from app_social.infrastructure.database.persistent_model.message_po import MessagePO
from app_travel.infrastructure.database.persistent_model.trip_po import TripPO, TripMemberPO, TripDayPO, ActivityPO, TransitPO

# 资源注册表：将 URL 中的 resource_name 映射到 SQLAlchemy PO 类
RESOURCE_MAP = {
    'users': UserPO,
    'posts': PostPO,
    'comments': CommentPO,
    'likes': LikePO,
    'post_images': PostImagePO,
    'post_tags': PostTagPO,
    'conversations': ConversationPO,
    'messages': MessagePO,
    'trips': TripPO,
    'trip_members': TripMemberPO,
    'trip_days': TripDayPO,
    'activities': ActivityPO,
    'transits': TransitPO
}

def get_model_class(resource_name: str):
    """根据资源名称获取对应的 PO 类"""
    return RESOURCE_MAP.get(resource_name)
