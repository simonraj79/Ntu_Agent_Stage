# app/routes/main.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Agent, Conversation

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    if current_user.is_faculty:
        return faculty_dashboard()
    return student_dashboard()

def faculty_dashboard():
    total_agents = Agent.query.filter_by(creator_id=current_user.id).count()
    total_conversations = Conversation.query.join(Agent).filter(Agent.creator_id == current_user.id).count()
    recent_conversations = Conversation.query.join(Agent).filter(Agent.creator_id == current_user.id).order_by(Conversation.updated_at.desc()).limit(5).all()

    return render_template('faculty_dashboard.html', 
                           total_agents=total_agents, 
                           total_conversations=total_conversations, 
                           recent_conversations=recent_conversations)

@bp.route('/student-dashboard')
@login_required
def student_dashboard():
    available_agents = Agent.query.filter_by(is_public=True).all()
    recent_conversations = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.updated_at.desc()).limit(5).all()

    # Get the 3 most recently created public agents
    featured_agents = Agent.query.filter_by(is_public=True).order_by(Agent.created_at.desc()).limit(3).all()

    return render_template('student_dashboard.html', 
                           available_agents=available_agents, 
                           recent_conversations=recent_conversations,
                           featured_agents=featured_agents)
