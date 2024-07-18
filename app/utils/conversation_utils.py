from app.models.conversation import ChatLog

def get_conversation_preview(conversation_id):
    first_message = ChatLog.query.filter_by(conversation_id=conversation_id).order_by(ChatLog.timestamp).first()
    if first_message:
        return first_message.user_message[:50] + '...' if len(first_message.user_message) > 50 else first_message.user_message
    return "No messages"
