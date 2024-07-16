from flask import Blueprint, render_template, request, jsonify, stream_with_context, Response, url_for, flash, redirect
from flask_login import login_required, current_user
from app.models import Agent, ChatLog, AgentCategory, AgentCollaborators, User, Conversation, ConversationInsights, get_conversation_preview
from app import db
from config import Config
from openai import OpenAI, OpenAIError
import traceback
from sqlalchemy import or_, func
from datetime import datetime, timedelta
from app.forms import AgentForm, DeleteAgentForm

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

@bp.route('/agent-directory')
@login_required
def agent_directory():
    user_agents = Agent.query.filter(or_(Agent.creator_id == current_user.id, 
                                         Agent.collaborators.any(user_id=current_user.id))).all()
    other_agents = Agent.query.filter(Agent.creator_id != current_user.id, 
                                      Agent.is_public == True).all()
    categories = AgentCategory.query.all()
    return render_template('agent_directory.html', user_agents=user_agents, 
                           other_agents=other_agents, categories=categories)

@bp.route('/create-agent', methods=['GET', 'POST'])
@login_required
def create_agent():
    form = AgentForm()
    if form.validate_on_submit():
        agent = Agent(
            name=form.name.data,
            description=form.description.data,
            system_prompt=form.system_prompt.data,
            creator_id=current_user.id,
            category_id=form.category_id.data,  # Changed from category to category_id
            is_public=form.is_public.data
        )
        db.session.add(agent)
        db.session.commit()
        flash('Agent created successfully!', 'success')
        return redirect(url_for('agents.agent_directory'))
    
    return render_template('create_agent.html', form=form)

@bp.route('/chat/<int:agent_id>', methods=['GET', 'POST'])
@login_required
def chat(agent_id):
    agent = Agent.query.get_or_404(agent_id)
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

            def generate_response():
                messages = [
                    {"role": "system", "content": agent.system_prompt},
                    {"role": "user", "content": user_message}
                ]
                try:
                    print(f"OpenAI API Key: {mask_api_key(Config.OPENAI_API_KEY)}")
                    print("Sending request to OpenAI API...")
                    stream = client.chat.completions.create(
                        model="gpt-3.5-turbo",
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

            return Response(stream_with_context(generate_response()), content_type='text/event-stream')

    return render_template('chat.html', agent=agent)

@bp.route('/conversation-history')
@login_required
def conversation_history():
    page = request.args.get('page', 1, type=int)
    agent_id = request.args.get('agent')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Conversation.query.filter_by(user_id=current_user.id)

    if agent_id:
        query = query.filter_by(agent_id=int(agent_id))
    if start_date:
        query = query.filter(Conversation.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Conversation.created_at <= datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))

    conversations = query.order_by(Conversation.updated_at.desc()).paginate(page=page, per_page=10)
    agents = Agent.query.all()

    return render_template('conversation_history.html', 
                           conversations=conversations, 
                           agents=agents,
                           current_filters={
                               'agent': agent_id,
                               'start_date': start_date,
                               'end_date': end_date
                           })


@bp.route('/edit-agent/<int:agent_id>', methods=['GET', 'POST'])
@login_required
def edit_agent(agent_id):
    print(f"Editing agent with id: {agent_id}")  # Debug log
    agent = Agent.query.get_or_404(agent_id)
    if agent.creator_id != current_user.id:
        flash('You do not have permission to edit this agent.')
        return redirect(url_for('agents.agent_directory'))
    
    form = AgentForm(obj=agent)
    if form.validate_on_submit():
        print("Form submitted and validated")  # Debug log
        form.populate_obj(agent)
        agent.category_id = form.category_id.data  # Manually set the category_id
        db.session.commit()
        flash('Agent updated successfully.')
        return redirect(url_for('agents.agent_directory'))
    
    return render_template('edit_agent.html', form=form, agent=agent, delete_form=DeleteAgentForm())

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

    flash('Invalid request.')
    return redirect(url_for('agents.edit_agent', agent_id=agent_id))

@bp.route('/conversation/<int:conversation_id>')
@login_required
def view_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    if conversation.user_id != current_user.id and not current_user.is_faculty:
        flash('You do not have permission to view this conversation.')
        return redirect(url_for('agents.conversation_history'))
    
    chat_logs = ChatLog.query.filter_by(conversation_id=conversation_id).order_by(ChatLog.timestamp).all()
    for log in chat_logs:
        print(f"User message: {log.user_message}")
        print(f"AI response: {log.ai_response}")
    return render_template('view_conversation.html', conversation=conversation, chat_logs=chat_logs)

@bp.route('/generate-insights/<int:conversation_id>', methods=['POST'])
@login_required
def generate_insights(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    if not current_user.is_faculty and conversation.agent.creator_id != current_user.id:
        return jsonify({'error': 'You do not have permission to generate insights for this conversation.'}), 403

    chat_logs = ChatLog.query.filter_by(conversation_id=conversation_id).order_by(ChatLog.timestamp).all()
    full_conversation = "\n".join([f"User: {log.user_message}\nAI: {log.ai_response}" for log in chat_logs])

    print(f"Full conversation: {full_conversation}")  # Log the full conversation

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Analyze the following conversation and provide insights. Your response should be in this exact format:\nTopics: topic1, topic2, topic3\nSentiment: [a number between -1 and 1]\nSummary: A brief summary of the conversation."},
                {"role": "user", "content": full_conversation}
            ]
        )

        insights_text = response.choices[0].message.content
        print(f"Raw insights: {insights_text}")  # Log the raw insights

        topics, sentiment, summary = parse_insights(insights_text)

        print(f"Parsed insights: Topics: {topics}, Sentiment: {sentiment}, Summary: {summary}")  # Log the parsed insights

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
        print(f"Error generating insights: {str(e)}")  # Log any errors
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
            summary = ':'.join(line.split(':')[1:]).strip()  # In case the summary contains colons

    return topics, sentiment, summary
