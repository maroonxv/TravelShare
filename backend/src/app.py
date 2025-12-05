from flask import Flask
from flask_cors import CORS
import os

# 导入共享数据库配置
from shared.database.core import engine, Base

# 导入所有 PO 模块以注册到 Base
# Auth
from app_auth.infrastructure.database.persistent_model.user_po import UserPO
# Social
from app_social.infrastructure.database.persistent_model.post_po import PostPO, CommentPO, LikePO
from app_social.infrastructure.database.persistent_model.conversation_po import ConversationPO
from app_social.infrastructure.database.persistent_model.message_po import MessagePO
# Travel
from app_travel.infrastructure.database.persistent_model.trip_po import TripPO, TripMemberPO, TripDayPO, ActivityPO

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # 初始化数据库表
    # 在实际生产环境中，建议使用 Alembic 进行数据库迁移，而不是 create_all
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized.")
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
