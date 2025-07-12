import json
from Scholarly import db, app, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    notes = db.relationship('Notes', backref='author', lazy=True)
    quizzes = db.relationship('Quiz', backref='author', lazy=True)

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(), nullable=False)
    content = db.Column(db.String(20000), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    quizzes = db.relationship('Quiz', backref='note', lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    title = db.Column(db.String(), nullable=False)
    model_used = db.Column(db.String(50), nullable=False, default='Groq')
    questions_json = db.Column(db.Text(), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def get_questions(self):
        try:
            return json.loads(self.questions_json)
        except json.JSONDecodeError:
            return []