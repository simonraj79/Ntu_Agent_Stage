from datetime import datetime
from app import db

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    is_public = db.Column(db.Boolean, default=False)
    use_count = db.Column(db.Integer, default=0)
    category = db.relationship('AgentCategory', backref='agents')
    collaborators = db.relationship('AgentCollaborators', back_populates='agent', cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='agent', lazy='dynamic')

class AgentCollaborators(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permission_level = db.Column(db.String(20), nullable=False)
    agent = db.relationship('Agent', back_populates='collaborators')
    user = db.relationship('User', backref='collaborations')
