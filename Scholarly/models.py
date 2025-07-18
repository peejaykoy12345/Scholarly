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
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True)

    flashcards = db.relationship('Flashcards', backref="author", lazy=True)

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(), nullable=False)
    content = db.Column(db.String(20000), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    quizzes = db.relationship('Quiz', backref='note', lazy=True)
    flashcards = db.relationship('Flashcards', backref='note', lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    title = db.Column(db.String(), nullable=False)
    model_used = db.Column(db.String(50), nullable=False, default='Groq')
    quiz_type = db.Column(db.String(20), nullable=False)
    answer_format = db.Column(db.String(20), nullable=True, server_default="Multiple Choice")
    questions_json = db.Column(db.Text(), nullable=False)
    results = db.relationship('QuizResult', backref='quiz', lazy=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def get_questions(self):
        try:
            return json.loads(self.questions_json)
        except json.JSONDecodeError:
            return []
        
    def get_question_count(self):
        return sum(len(group['output']) for group in self.get_questions())
        
class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    
    question = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    user_answer = db.Column(db.String(255), nullable=False)
    explanation = db.Column(db.Text)
    
    is_correct = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Flashcards(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)

    title = db.Column(db.String(), nullable=False)

    flashcards_json = db.Column(db.Text(), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def get_flashcards(self):
        try:
            return json.loads(self.flashcards_json)
        except json.JSONDecodeError:
            return []