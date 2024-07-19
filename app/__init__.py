# app/__init__.py
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import exc
from config import Config
import time
import logging
from .nav_config import NAV_ITEMS
from .db import db
from app.models import User

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
csrf = CSRFProtect()

def add_default_categories(app):
    with app.app_context():
        from app.models import AgentCategory
        categories = [
            "Engineering", "Science", "Business", "Humanities", "Arts",
            "Medicine", "Computing", "Education", "Communication", "Design",
            "Sports", "Sustainability", "Technology", "Innovation", "Research",
            "International", "Entrepreneurship", "Leadership"
        ]
        for category_name in categories:
            category = AgentCategory.query.filter_by(name=category_name).first()
            if not category:
                new_category = AgentCategory(name=category_name)
                db.session.add(new_category)
        db.session.commit()
        logger.info("Default categories added successfully.")

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        retry_count = 0
        while retry_count < 3:
            try:
                from app.models import User, Agent, AgentCategory, AgentCollaborators, ChatLog, Conversation, ConversationInsights
                db.create_all()
                add_default_categories(app)
                logger.info("Database initialized successfully.")
                break
            except exc.OperationalError as e:
                retry_count += 1
                logger.warning(f"Database connection failed. Retrying in 5 seconds... (Attempt {retry_count}/3)")
                time.sleep(5)
        else:
            logger.error("Failed to connect to the database after 3 attempts.")
            raise

    # Delayed import of blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.main import bp as main_bp
    from app.routes.agents import bp as agents_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(agents_bp)
    logger.info("Blueprints registered successfully.")

    @app.context_processor
    def inject_nav_items():
        return dict(nav_items=NAV_ITEMS)

    @app.context_processor
    def utility_processor():
        from app.utils.conversation_utils import get_conversation_preview
        return dict(get_conversation_preview=get_conversation_preview)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    logger.info("Application created successfully.")
    return app
