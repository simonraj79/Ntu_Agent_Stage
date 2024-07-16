# app/nav_config.py

NAV_ITEMS = [
    {'name': 'Home', 'url': 'main.index', 'auth_required': False},
    {'name': 'Agent Directory', 'url': 'agents.agent_directory', 'auth_required': True},
    {'name': 'Conversation History', 'url': 'agents.conversation_history', 'auth_required': True},
]