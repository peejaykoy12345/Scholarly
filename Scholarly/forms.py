from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, SelectField, TextAreaField, IntegerField
from flask_wtf.file import FileAllowed
from wtforms.validators import DataRequired, length, EqualTo, ValidationError, Email, NumberRange
from Scholarly.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), length(min=2, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password =  PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

    def validate_username(self, username):

        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is taken')

    def validate_email(self, email):

        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is taken')
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password =  PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

class AccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), length(min=2, max=15)])
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

class CreateNoteForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Create")

class CreateAINotes(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    type = SelectField(
        'Select how you want your notes to be made',
        choices=[('Summarize', 'Summarize'), ('Cornell method', 'Cornell method')],
        validators=[DataRequired()]
    )
    file = FileField(
        'Upload image or PDF',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images or PDFs only!')]
    )
    submit = SubmitField("Create notes")

class CreateQuizForm(FlaskForm):
    note = SelectField('Select Note', coerce=int, validators=[DataRequired()])
    model = SelectField('Select Model', choices=[('Groq', 'Groq')], validators=[DataRequired()])
    quiz_type = SelectField('Select quiz type', choices=[('Identification', 'Identification'), ('Situational', 'Situational')], validators=[DataRequired()])
    answer_format = SelectField('Select question format', choices=[("Multiple Choice", "Multiple Choice"), ("No Choices", "No Choices"), ("Essay form", "Essay form")], validators=[DataRequired()])
    question_count = IntegerField('Input how many questions you want', validators=[DataRequired(), NumberRange(min=1, max=30)])
    submit = SubmitField('Generate')

class CreateFlashCardsForm(FlaskForm):
    note = SelectField('Select Note', coerce=int, validators=[DataRequired()])
    model = SelectField('Select Model', choices=[('Groq', 'Groq')], validators=[DataRequired()])
    flashcards_count = IntegerField('Input how many questions you want', validators=[DataRequired(), NumberRange(min=1, max=30)])
    submit = SubmitField('Generate')
