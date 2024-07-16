# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, PasswordField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
from app.models import AgentCategory

class AgentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description', validators=[DataRequired()])
    system_prompt = TextAreaField('System Prompt', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int)
    is_public = BooleanField('Make this agent public')
    temperature = DecimalField('Temperature (Creativity)', default=0.5, places=1, validators=[NumberRange(min=0, max=1)], 
                               description='0 = Focused and deterministic, 1 = Creative and random')

    def __init__(self, *args, **kwargs):
        super(AgentForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in AgentCategory.query.order_by('name')]

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('student', 'Student'), ('faculty', 'Faculty')], validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('student', 'Student'), ('faculty', 'Faculty')], validators=[DataRequired()])
    submit = SubmitField('Register')
class DeleteAgentForm(FlaskForm):
    submit = SubmitField('Delete Agent')
