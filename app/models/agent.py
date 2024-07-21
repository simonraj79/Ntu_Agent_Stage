#app\models\agent.py
from enum import Enum
from app.db import db
from datetime import datetime
import secrets

class AccessLevel(Enum):
    PUBLIC = 'Public'
    SECRET_LINK = 'Secret Link'
    PRIVATE = 'Private'

class AgentCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    system_prompt = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('agent_category.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_used = db.Column(db.DateTime)
    access_level = db.Column(db.Enum(AccessLevel), default=AccessLevel.PRIVATE)
    temperature = db.Column(db.Float, default=0.5)
    use_count = db.Column(db.Integer, default=0)
    secret_link = db.Column(db.String(128), unique=True)
    sharable_link = db.Column(db.String(128), unique=True)  # New field for public agent sharable link
    
    category = db.relationship('AgentCategory', backref='agents')
    collaborators = db.relationship('AgentCollaborators', back_populates='agent', cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='agent', lazy='dynamic')
    
    def generate_secret_link(self):
        self.secret_link = secrets.token_urlsafe(16)

    def generate_sharable_link(self):
        self.sharable_link = secrets.token_urlsafe(16)

    def regenerate_secret_link(self):
        self.generate_secret_link()
        db.session.commit()

    def regenerate_sharable_link(self):
        self.generate_sharable_link()
        db.session.commit()

    def disable_secret_link(self):
        self.secret_link = None
        db.session.commit()

    def disable_sharable_link(self):
        self.sharable_link = None
        db.session.commit()

class AgentCollaborators(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permission_level = db.Column(db.String(20), nullable=False)
    agent = db.relationship('Agent', back_populates='collaborators')
    user = db.relationship('User', backref='collaborations')