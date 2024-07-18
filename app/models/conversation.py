from datetime import datetime
from app import db
from app.db import db

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
