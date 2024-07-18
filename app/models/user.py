from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.agent import Agent
from app.models.conversation import ChatLog
from app.db import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    display_name = db.Column(db.String(64))
    profile_picture = db.Column(db.String(256))
    bio = db.Column(db.Text)
    is_faculty = db.Column(db.Boolean, default=False)
    agents = db.relationship('Agent', backref='creator', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_agent_chat_logs(self):
        return ChatLog.query.join(Agent).filter(Agent.creator_id == self.id)
