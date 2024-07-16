#app\models.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime

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

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    chat_logs = db.relationship('ChatLog', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    insights = db.relationship('ConversationInsights', backref='conversation', uselist=False, cascade='all, delete-orphan')

class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='chat_logs')
    agent = db.relationship('Agent', backref='chat_logs')

class ConversationInsights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    topics = db.Column(db.ARRAY(db.String))
    sentiment = db.Column(db.Float)
    summary = db.Column(db.Text)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

def get_conversation_preview(conversation_id):
    first_message = ChatLog.query.filter_by(conversation_id=conversation_id).order_by(ChatLog.timestamp).first()
    if first_message:
        return first_message.user_message[:50] + '...' if len(first_message.user_message) > 50 else first_message.user_message
    return "No messages"