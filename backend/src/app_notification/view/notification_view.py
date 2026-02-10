"""
通知 REST API
"""
from flask import Blueprint, request, jsonify, g, session
import traceback

from shared.database.core import SessionLocal
from app_notification.infrastructure.database.dao_impl.sqlalchemy_notification_dao import SQLAlchemyNotificationDAO
from app_notification.infrastructure.database.repository_impl.notification_repository_impl import NotificationRepositoryImpl
from app_notification.services.notification_service import NotificationService

# 创建蓝图
notification_bp = Blueprint('notification', __name__, url_prefix='/api/notifications')


@notification_bp.before_request
def create_session():
    """每个请求开始前创建数据库会话"""
    g.session = SessionLocal()


@notification_bp.teardown_request
def shutdown_session(exception=None):
    """请求结束时关闭数据库会话"""
    if hasattr(g, 'session'):
        g.session.close()


def get_notification_service() -> NotificationService:
    """获取 NotificationService 实例"""
    dao = SQLAlchemyNotificationDAO(g.session)
    repo = NotificationRepositoryImpl(dao)
    return NotificationService(repo)


@notification_bp.route('', methods=['GET'])
def list_notifications():
    """获取当前用户通知列表"""
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    service = get_notification_service()
    
    try:
        notifications = service.get_notifications(current_user_id, limit, offset)
        return jsonify(notifications)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500


@notification_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    """获取未读通知数量"""
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    service = get_notification_service()
    
    try:
        count = service.get_unread_count(current_user_id)
        return jsonify({'count': count})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500


@notification_bp.route('/<notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    """标记单条通知已读"""
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    service = get_notification_service()
    
    try:
        success = service.mark_read(notification_id, current_user_id)
        
        if success:
            g.session.commit()
            return jsonify({'message': 'Notification marked as read'})
        else:
            return jsonify({'error': 'Notification not found'}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500


@notification_bp.route('/read-all', methods=['PUT'])
def mark_all_read():
    """标记全部通知已读"""
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    service = get_notification_service()
    
    try:
        count = service.mark_all_read(current_user_id)
        g.session.commit()
        return jsonify({'message': f'{count} notifications marked as read', 'count': count})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500
