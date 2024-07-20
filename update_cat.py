from app import db
from app.models import AgentCategory

new_categories = [
    AgentCategory(name="Interdisciplinary", description="Spans multiple disciplines"),
    AgentCategory(name="CITS", description="Computer and Information Technology Services"),
    AgentCategory(name="HR", description="Human Resources"),
    AgentCategory(name="NSS", description="NTU Student Services")
]

db.session.add_all(new_categories)
db.session.commit()