"""
通知事件处理器

订阅领域事件并创建相应的通知。
"""
from shared.event_bus import EventBus
from shared.database.core import SessionLocal
from app_notification.domain.entity.notification import Notification
from app_notification.domain.value_objects.notification_value_objects import NotificationType
from app_notification.infrastructure.database.dao_impl.sqlalchemy_notification_dao import SQLAlchemyNotificationDAO
from app_notification.infrastructure.database.repository_impl.notification_repository_impl import NotificationRepositoryImpl
from app_notification.infrastructure.database.persistent_model.notification_po import NotificationPO


def register_notification_handlers():
    """注册所有通知事件处理器"""
    event_bus = EventBus.get_instance()
    
    # 好友请求
    event_bus.subscribe('FriendRequestSentEvent', handle_friend_request_sent)
    
    # 好友接受
    event_bus.subscribe('FriendshipAcceptedEvent', handle_friendship_accepted)
    
    # 行程邀请
    event_bus.subscribe('TripMemberAddedEvent', handle_trip_member_added)
    
    # 帖子点赞
    event_bus.subscribe('PostLikedEvent', handle_post_liked)
    
    # 帖子评论
    event_bus.subscribe('CommentAddedEvent', handle_comment_added)
    
    # 费用添加
    event_bus.subscribe('ExpenseAddedEvent', handle_expense_added)


def handle_friend_request_sent(event):
    """处理好友请求事件"""
    session = SessionLocal()
    try:
        notification = Notification.create(
            user_id=event.to_user_id,
            notification_type=NotificationType.FRIEND_REQUEST,
            title="新的好友请求",
            content=f"用户向你发送了好友请求",
            resource_type="user",
            resource_id=event.from_user_id,
            actor_id=event.from_user_id
        )
        
        dao = SQLAlchemyNotificationDAO(session)
        repo = NotificationRepositoryImpl(dao)
        repo.save(notification)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error handling friend request event: {e}")
    finally:
        session.close()


def handle_friendship_accepted(event):
    """处理好友接受事件"""
    session = SessionLocal()
    try:
        notification = Notification.create(
            user_id=event.requester_id,
            notification_type=NotificationType.FRIEND_ACCEPTED,
            title="好友请求已接受",
            content=f"用户接受了你的好友请求",
            resource_type="user",
            resource_id=event.accepter_id,
            actor_id=event.accepter_id
        )
        
        dao = SQLAlchemyNotificationDAO(session)
        repo = NotificationRepositoryImpl(dao)
        repo.save(notification)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error handling friendship accepted event: {e}")
    finally:
        session.close()


def handle_trip_member_added(event):
    """处理行程成员添加事件"""
    session = SessionLocal()
    try:
        # 只有当不是自己添加自己时才发送通知
        if event.user_id != event.added_by:
            notification = Notification.create(
                user_id=event.user_id,
                notification_type=NotificationType.TRIP_INVITE,
                title="行程邀请",
                content=f"你被邀请加入行程",
                resource_type="trip",
                resource_id=event.trip_id,
                actor_id=event.added_by
            )
            
            dao = SQLAlchemyNotificationDAO(session)
            repo = NotificationRepositoryImpl(dao)
            repo.save(notification)
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error handling trip member added event: {e}")
    finally:
        session.close()


def handle_post_liked(event):
    """处理帖子点赞事件"""
    session = SessionLocal()
    try:
        # 不给自己发通知
        if event.user_id != event.post_author_id:
            notification = Notification.create(
                user_id=event.post_author_id,
                notification_type=NotificationType.POST_LIKED,
                title="帖子获得点赞",
                content=f"用户点赞了你的帖子",
                resource_type="post",
                resource_id=event.post_id,
                actor_id=event.user_id
            )
            
            dao = SQLAlchemyNotificationDAO(session)
            repo = NotificationRepositoryImpl(dao)
            repo.save(notification)
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error handling post liked event: {e}")
    finally:
        session.close()


def handle_comment_added(event):
    """处理评论添加事件"""
    session = SessionLocal()
    try:
        # 不给自己发通知
        if event.user_id != event.post_author_id:
            notification = Notification.create(
                user_id=event.post_author_id,
                notification_type=NotificationType.POST_COMMENTED,
                title="帖子收到评论",
                content=f"用户评论了你的帖子",
                resource_type="post",
                resource_id=event.post_id,
                actor_id=event.user_id
            )
            
            dao = SQLAlchemyNotificationDAO(session)
            repo = NotificationRepositoryImpl(dao)
            repo.save(notification)
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error handling comment added event: {e}")
    finally:
        session.close()


def handle_expense_added(event):
    """处理费用添加事件"""
    session = SessionLocal()
    try:
        # 获取行程的所有成员（除了付款人）
        from app_travel.infrastructure.database.dao_impl.sqlalchemy_trip_dao import SqlAlchemyTripDao
        from app_travel.domain.value_objects.travel_value_objects import TripId
        
        trip_dao = SqlAlchemyTripDao(session)
        trip_po = trip_dao.get_by_id(event.trip_id)
        
        if trip_po:
            trip = trip_po.to_domain()
            for member in trip.members:
                # 不给付款人自己发通知
                if member.user_id != event.payer_id:
                    notification = Notification.create(
                        user_id=member.user_id,
                        notification_type=NotificationType.EXPENSE_ADDED,
                        title="新增费用",
                        content=f"行程中添加了新的费用: {event.description}",
                        resource_type="expense",
                        resource_id=event.expense_id,
                        actor_id=event.payer_id
                    )
                    
                    dao = SQLAlchemyNotificationDAO(session)
                    repo = NotificationRepositoryImpl(dao)
                    repo.save(notification)
            
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error handling expense added event: {e}")
    finally:
        session.close()
