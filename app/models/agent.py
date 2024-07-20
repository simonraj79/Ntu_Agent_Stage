#app\models\agent.py
from enum import Enum
from app.db import db
from datetime import datetime
import secrets

class AccessLevel(Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'
    FACULTY = 'faculty'

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
    sharing_link = db.Column(db.String(64), unique=True)
    
    category = db.relationship('AgentCategory', backref='agents')
    collaborators = db.relationship('AgentCollaborators', back_populates='agent', cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='agent', lazy='dynamic')

    def generate_sharing_link(self):
        self.sharing_link = secrets.token_urlsafe(32)

    def regenerate_sharing_link(self):
        self.generate_sharing_link()
        db.session.commit()

    def disable_sharing_link(self):
        self.sharing_link = None
        db.session.commit()

class AgentCollaborators(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permission_level = db.Column(db.String(20), nullable=False)
    agent = db.relationship('Agent', back_populates='collaborators')
    user = db.relationship('User', backref='collaborations')