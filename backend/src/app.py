import os
from typing import Any, Mapping, Optional

from flask import Flask
from flask_cors import CORS
from sqlalchemy.exc import OperationalError

from shared.database.core import Base, engine

# Import all persistent models so SQLAlchemy registers them before create_all.
from app_admin import admin_bp
from app_ai import ai_bp
from app_auth.infrastructure.database.persistent_model.user_po import UserPO
from app_auth.view.auth_view import auth_bp
from app_notification.infrastructure.database.persistent_model.notification_po import NotificationPO
from app_notification.view.notification_view import notification_bp
from app_social.infrastructure.database.persistent_model.conversation_po import ConversationPO
from app_social.infrastructure.database.persistent_model.message_po import MessagePO
from app_social.infrastructure.database.po.friendship_po import FriendshipPO
from app_social.infrastructure.database.persistent_model.post_po import CommentPO, LikePO, PostPO
from app_social.infrastructure.socket.handlers import register_social_socket_handlers
from app_social.view.social_view import social_bp
from app_travel.infrastructure.database.persistent_model.expense_po import (
    ExpensePO,
    ExpenseSharePO,
    SettlementTransferPO,
)
from app_travel.infrastructure.database.persistent_model.template_po import TripTemplatePO
from app_travel.infrastructure.database.persistent_model.trip_po import (
    ActivityPO,
    TransitPO,
    TripDayPO,
    TripMemberPO,
    TripPO,
)
from app_travel.view.travel_view import travel_bp
from shared.infrastructure.socket import socketio


def create_app(config: Optional[Mapping[str, Any]] = None):
    app = Flask(__name__, static_url_path="/static", static_folder="static")
    if config:
        app.config.update(config)

    app.secret_key = (
        app.config.get("SECRET_KEY")
        or os.getenv("FLASK_SECRET_KEY")
        or "travel-sharing-dev-secret"
    )
    CORS(app, supports_credentials=True)

    socketio.init_app(app)
    register_social_socket_handlers()

    upload_dir = os.path.join(app.static_folder, "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    should_initialize_database = app.config.get("INITIALIZE_DATABASE", True)
    is_pytest_context = bool(os.getenv("PYTEST_CURRENT_TEST"))
    if should_initialize_database:
        print("Initializing database tables...")
        try:
            Base.metadata.create_all(bind=engine)
            print("Database tables initialized.")
        except OperationalError:
            if app.config.get("TESTING") or is_pytest_context:
                print(
                    "Skipping database initialization during tests because the configured database is unavailable."
                )
            else:
                raise

    app.register_blueprint(travel_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_bp)

    @app.route("/health")
    def health_check():
        return {"status": "healthy"}

    return app


if __name__ == "__main__":
    app = create_app()
    socketio.run(app, debug=True, port=5001)
