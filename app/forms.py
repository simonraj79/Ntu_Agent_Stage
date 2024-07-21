# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
from app.models.agent import AccessLevel

class AgentForm(FlaskForm):
    name = StringField('Agent Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description', validators=[DataRequired()])
    system_prompt = TextAreaField('Initial Instructions', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    access_level = SelectField('Access Level', choices=[
        (AccessLevel.PUBLIC.name, 'Public - Anyone in the organisation'),
        (AccessLevel.SECRET_LINK.name, 'Secret Link - Students or faculty with the link'),
        (AccessLevel.PRIVATE.name, 'Private - Only the creator')
    ], validators=[DataRequired()])
    temperature = DecimalField('Temperature (Creativity)', default=0.5, places=1, validators=[NumberRange(min=0, max=1)], 
                               description='0 = Focused and deterministic, 1 = Creative and random')
    submit = SubmitField('Create Agent')

    def __init__(self, *args, **kwargs):
        super(AgentForm, self).__init__(*args, **kwargs)
        from app.models import AgentCategory
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