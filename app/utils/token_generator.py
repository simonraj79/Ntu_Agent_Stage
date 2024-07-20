import secrets
from flask import url_for

def generate_share_token():
    return secrets.token_urlsafe(32)

def create_share_url(token):
    return url_for('agents.access_shared_agent', token=token, _external=True)