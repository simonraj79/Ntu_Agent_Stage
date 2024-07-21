# app/routes/agents.py
from flask import Blueprint, render_template, request, jsonify, stream_with_context, Response, url_for, flash, redirect, current_app
from flask_login import login_required, current_user
from app.models import Agent, ChatLog, AgentCategory, AgentCollaborators, User, Conversation, ConversationInsights
from app import db
from config import Config
from openai import OpenAI, OpenAIError
import traceback
from sqlalchemy import or_, func
from datetime import datetime, timedelta
from app.forms import AgentForm, DeleteAgentForm
from app.models.agent import AccessLevel
from urllib.parse import urlencode




bp = Blueprint('agents', __name__)

client = OpenAI(api_key=Config.OPENAI_API_KEY)

def mask_api_key(api_key):
    if api_key:
        return f"{api_key[:4]}...{api_key[-4:]}"
    return "Not set"

@bp.route('/agent-reports')
@login_required
def agent_reports():
    page = request.args.get('page', 1, type=int)
    chat_logs = ChatLog.query.filter_by(user_id=current_user.id).order_by(ChatLog.timestamp.desc()).paginate(page=page, per_page=10)
    return render_template('agent_reports.html', chat_logs=chat_logs)


@bp.route('/create-agent', methods=['GET', 'POST'])
@login_required
def create_agent():
    form = AgentForm()
    if form.validate_on_submit():
        try:
            agent = Agent(
                name=form.name.data,
                description=form.description.data,
                system_prompt=form.system_prompt.data,
                creator_id=current_user.id,
                category_id=form.category_id.data,
                access_level=AccessLevel[form.access_level.data],
                temperature=form.temperature.data
            )
            if agent.access_level == AccessLevel.SECRET_LINK:
                agent.generate_secret_link()
            db.session.add(agent)
            db.session.commit()
            flash('Agent created successfully!', 'success')
            return redirect(url_for('agents.agent_directory'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating agent: {str(e)}")
            flash(f'Error creating agent: {str(e)}', 'error')
    return render_template('create_agent.html', form=form, title="Create New Agent")

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.models import Agent, AgentCategory
from app import db
from app.forms import AgentForm, DeleteAgentForm
from app.models.agent import AccessLevel  # Make sure to import AccessLevel

# ... other imports and route definitions ...

@bp.route('/edit-agent/<int:agent_id>', methods=['GET', 'POST'])
@login_required
def edit_agent(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    if agent.creator_id != current_user.id:
        flash('You do not have permission to edit this agent.', 'error')
        return redirect(url_for('agents.agent_directory'))
    
    form = AgentForm(obj=agent)
    form.category_id.choices = [(c.id, c.name) for c in AgentCategory.query.all()]
    
    if form.validate_on_submit():
        form.populate_obj(agent)
        agent.access_level = AccessLevel[form.access_level.data]
        if agent.access_level == AccessLevel.SECRET_LINK and not agent.secret_link:
            agent.generate_secret_link()
        elif agent.access_level != AccessLevel.SECRET_LINK:
            agent.secret_link = None
        try:
            db.session.commit()
            flash('Agent updated successfully.', 'success')
            return redirect(url_for('agents.agent_directory'))  # Redirect to agent directory instead
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating agent: {str(e)}")
            flash(f'Error updating agent: {str(e)}', 'error')
    
    return render_template('edit_agent.html', form=form, agent=agent, AccessLevel=AccessLevel)

@bp.route('/regenerate-link/<int:agent_id>', methods=['POST'])
@login_required
def regenerate_link(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    if agent.creator_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    agent.regenerate_secret_link()
    return jsonify({'new_link': agent.secret_link})

@bp.route('/secret-agent/<string:token>')
@login_required
def access_secret_agent(token):
    agent = Agent.query.filter_by(secret_link=token).first_or_404()
    return redirect(url_for('agents.chat', agent_id=agent.id))

def can_access_agent(agent, user):
    if agent.access_level == AccessLevel.PUBLIC:
        return True
    if agent.access_level == AccessLevel.PRIVATE:
        return agent.creator_id == user.id
    if agent.access_level == AccessLevel.SECRET_LINK:
        return True  # The access is controlled by the secret link itself
    return False

@bp.route('/get-secret-link/<int:agent_id>')
@login_required
def get_secret_link(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    if agent.creator_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    if agent.access_level != AccessLevel.SECRET_LINK:
        return jsonify({'error': 'This agent does not have a secret link'}), 400
    if not agent.secret_link:
        agent.generate_secret_link()
        db.session.commit()
    return jsonify({'secret_link': url_for('agents.access_secret_agent', token=agent.secret_link, _external=True)})

def can_access_agent(agent, user):
    if agent.access_level == AccessLevel.PUBLIC:
        return True
    if agent.access_level == AccessLevel.PRIVATE:
        return agent.creator_id == user.id
    if agent.access_level == AccessLevel.SECRET_LINK:
        return True  # The access is controlled by the secret link itself
    return False

@bp.route('/agent-directory')
@login_required
def agent_directory():
    page = request.args.get('page', 1, type=int)
    
    user_agents = Agent.query.filter(
        or_(Agent.creator_id == current_user.id, 
            Agent.collaborators.any(user_id=current_user.id))
    ).order_by(Agent.created_at.desc()).paginate(page=page, per_page=12)
    
    other_agents = Agent.query.filter(
        Agent.creator_id != current_user.id,
        Agent.access_level == AccessLevel.PUBLIC
    ).order_by(Agent.created_at.desc()).limit(5).all()
    
    categories = AgentCategory.query.all()
    
    return render_template('agent_directory.html', 
                           user_agents=user_agents, 
                           other_agents=other_agents, 
                           categories=categories,
                           AccessLevel=AccessLevel)

@bp.route('/shared-agent/<string:token>')
@login_required
def access_shared_agent(token):
    agent = Agent.query.filter_by(sharing_link=token).first_or_404()
    return redirect(url_for('agents.chat', agent_id=agent.id))

@bp.route('/agent/<int:agent_id>')
@login_required
def agent_details(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    if agent.creator_id != current_user.id and agent.access_level != AccessLevel.PUBLIC:
        flash('You do not have permission to view this agent.', 'error')
        return redirect(url_for('agents.agent_directory'))
    # For now, we'll just redirect to the edit page
    return redirect(url_for('agents.edit_agent', agent_id=agent.id))

@bp.route('/chat/<int:agent_id>', methods=['GET', 'POST'])
@login_required
def chat(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    if not can_access_agent(agent, current_user):
        flash('You do not have permission to access this agent.', 'error')
        return redirect(url_for('agents.agent_directory'))
    if request.method == 'POST':
        user_message = request.json.get('message')
        if user_message:
            conversation = Conversation.query.filter_by(agent_id=agent.id, user_id=current_user.id).order_by(Conversation.updated_at.desc()).first()
            if not conversation or (datetime.utcnow() - conversation.updated_at) > timedelta(hours=1):
                conversation = Conversation(agent_id=agent.id, user_id=current_user.id)
                db.session.add(conversation)
                db.session.commit()
            
            chat_log = ChatLog(conversation_id=conversation.id, user_id=current_user.id, agent_id=agent.id, user_message=user_message)
            db.session.add(chat_log)
            agent.last_used = datetime.utcnow()
            agent.use_count += 1
            conversation.updated_at = datetime.utcnow()
            db.session.commit()

            return Response(stream_with_context(generate_response(agent, conversation, user_message, chat_log)), content_type='text/event-stream')

    conversation = Conversation.query.filter_by(agent_id=agent.id, user_id=current_user.id).order_by(Conversation.updated_at.desc()).first()
    chat_logs = []
    if conversation:
        chat_logs = ChatLog.query.filter_by(conversation_id=conversation.id).order_by(ChatLog.timestamp).all()
    
    return render_template('chat.html', agent=agent, chat_logs=chat_logs)

def can_access_agent(agent, user):
    if agent.access_level == AccessLevel.PUBLIC:
        return True
    if agent.access_level == AccessLevel.PRIVATE:
        return agent.creator_id == user.id
    if agent.access_level == AccessLevel.FACULTY:
        return user.is_faculty
    if agent.access_level == AccessLevel.CREATOR:
        return agent.creator_id == user.id
    return False

@bp.route('/chat/token/<string:access_token>')
@login_required
def chat_with_token(access_token):
    agent = Agent.query.filter_by(access_token=access_token).first_or_404()
    return chat(agent.id)

@bp.route('/chat/<int:agent_id>/clear', methods=['POST'])
@login_required
def clear_chat(agent_id):
    try:
        conversation = Conversation.query.filter_by(agent_id=agent_id, user_id=current_user.id).order_by(Conversation.updated_at.desc()).first()
        
        if conversation:
            new_conversation = Conversation(agent_id=agent_id, user_id=current_user.id)
            db.session.add(new_conversation)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Chat cleared successfully'})
        else:
            return jsonify({'success': False, 'error': 'No conversation found to clear'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

def generate_response(agent, conversation, user_message, chat_log):
    try:
        chat_logs = ChatLog.query.filter_by(conversation_id=conversation.id).order_by(ChatLog.timestamp).all()
        messages = [{"role": "system", "content": agent.system_prompt}]
        for log in chat_logs:
            messages.append({"role": "user", "content": log.user_message})
            if log.ai_response:
                messages.append({"role": "assistant", "content": log.ai_response})
        messages.append({"role": "user", "content": user_message})

        print(f"OpenAI API Key: {mask_api_key(Config.OPENAI_API_KEY)}")
        print("Sending request to OpenAI API...")
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
        )
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                text_chunk = chunk.choices[0].delta.content
                full_response += text_chunk
                print(f'Streamed chunk: {text_chunk}')
                yield f"data: {text_chunk}\n\n"
        print(f'Full AI response: {full_response}')
        chat_log.ai_response = full_response
        db.session.commit()
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)
        yield f"data: {error_message}\n\n"

@bp.route('/view-conversation/<int:conversation_id>')
@login_required
def view_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    if conversation.agent.creator_id != current_user.id:
        flash('You do not have permission to view this conversation.')
        return redirect(url_for('agents.conversation_history'))
    
    chat_logs = ChatLog.query.filter_by(conversation_id=conversation_id).order_by(ChatLog.timestamp).all()
    return render_template('view_conversation.html', conversation=conversation, chat_logs=chat_logs)



def update_url_params(args, updates):
    params = args.copy()
    for key, value in updates.items():
        if value is not None:
            params[key] = value
        else:
            params.pop(key, None)
    return urlencode(params)

@bp.route('/conversation-history')
@login_required
def conversation_history():
    if not current_user.is_faculty:
        flash('You do not have permission to view conversation history.')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    agent_id = request.args.get('agent')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Conversation.query.join(Agent).filter(Agent.creator_id == current_user.id)

    if agent_id:
        query = query.filter(Conversation.agent_id == int(agent_id))
    if start_date:
        query = query.filter(Conversation.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Conversation.created_at <= datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))

    conversations = query.order_by(Conversation.updated_at.desc()).paginate(page=page, per_page=10)
    agents = Agent.query.all()

    prev_url = url_for('agents.conversation_history') + '?' + update_url_params(request.args, {'page': conversations.prev_num}) if conversations.has_prev else None
    next_url = url_for('agents.conversation_history') + '?' + update_url_params(request.args, {'page': conversations.next_num}) if conversations.has_next else None

    return render_template('conversation_history.html', 
                           conversations=conversations, 
                           agents=agents,
                           current_filters={
                               'agent': agent_id,
                               'start_date': start_date,
                               'end_date': end_date
                           },
                           prev_url=prev_url,
                           next_url=next_url)


@bp.route('/delete-agent/<int:agent_id>', methods=['POST'])
@login_required
def delete_agent(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    if agent.creator_id != current_user.id:
        flash('You do not have permission to delete this agent.')
        return redirect(url_for('agents.agent_directory'))

    form = DeleteAgentForm()
    if form.validate_on_submit():
        db.session.delete(agent)
        db.session.commit()
        flash('Agent deleted successfully.')
        return redirect(url_for('agents.agent_directory'))

    flash('Failed to delete agent.')
    return redirect(url_for('agents.edit_agent', agent_id=agent_id))

@bp.route('/generate-insights/<int:conversation_id>', methods=['POST'])
@login_required
def generate_insights(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    if not current_user.is_faculty and conversation.agent.creator_id != current_user.id:
        return jsonify({'error': 'You do not have permission to generate insights for this conversation.'}), 403

    chat_logs = ChatLog.query.filter_by(conversation_id=conversation_id).order_by(ChatLog.timestamp).all()
    full_conversation = "\n".join([f"User: {log.user_message}\nAI: {log.ai_response}" for log in chat_logs])

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Analyze the following conversation and provide insights. Your response should be in this exact format:\nTopics: topic1, topic2, topic3\nSentiment: [a number between -1 and 1]\nSummary: A brief summary of the conversation."},
                {"role": "user", "content": full_conversation}
            ]
        )

        insights_text = response.choices[0].message.content

        topics, sentiment, summary = parse_insights(insights_text)

        conversation_insights = ConversationInsights.query.filter_by(conversation_id=conversation_id).first()
        if conversation_insights:
            db.session.delete(conversation_insights)

        conversation_insights = ConversationInsights(
            conversation_id=conversation_id,
            topics=topics,
            sentiment=sentiment,
            summary=summary,
            generated_at=datetime.utcnow()
        )
        db.session.add(conversation_insights)
        db.session.commit()

        return jsonify({
            'success': True, 
            'insights': {
                'topics': topics,
                'sentiment': sentiment,
                'summary': summary,
                'generated_at': conversation_insights.generated_at.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def parse_insights(insights_text):
    topics = []
    sentiment = 0.0
    summary = ""

    lines = insights_text.split('\n')
    for line in lines:
        if line.startswith("Topics:"):
            topics = [topic.strip() for topic in line.split(':')[1].split(',')]
        elif line.startswith("Sentiment:"):
            try:
                sentiment = float(line.split(':')[1].strip())
            except ValueError:
                pass
        elif line.startswith("Summary:"):
            summary = ':'.join(line.split(':')[1:]).strip()

    return topics, sentiment, summary

