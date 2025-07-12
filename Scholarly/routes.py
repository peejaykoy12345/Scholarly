import secrets, os
from flask import render_template, flash, redirect, request, url_for, session, abort
from flask_login import current_user, login_required, logout_user, login_user
from Scholarly import app, db, bcrypt
from Scholarly.models import User, Notes, Quiz
from Scholarly.forms import LoginForm, RegistrationForm, AccountForm, CreateNoteForm, CreateAINotes, CreateQuizForm
from PIL import Image
from werkzeug.utils import secure_filename
from AI.text_extracter import extract_text
from AI.summarize import summarize_text
from AI.quiz_gen.quiz_gen_groq import generate_questions as generate_questions_using_groq
from json import dumps

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit(): 
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login unsuccessful", 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data, 
            email = form.email.data, 
            password = hashed_password
        ) 
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created!', 'sucess')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/manually_create_notes', methods=["GET", "POST"])
@login_required
def manually_create_notes():
    form = CreateNoteForm()
    if form.validate_on_submit():
        note = Notes(
            owner_id=current_user.id,
            title=form.title.data,
            content=form.content.data
        )
        db.session.add(note)
        db.session.commit()
        flash("Your note has been created!", 'success')
        return redirect(url_for('notes'))
    return render_template('manually_create_notes.html', form=form)

@app.route('/create_ai_notes', methods=['GET', 'POST'])
@login_required
def create_ai_notes():
    form = CreateAINotes()
    if request.method == "POST":
        if 'confirm' in request.form:
            note = Notes(
                title=session.get('title'),
                content=session.get('summarized_text'),
                owner_id=current_user.id
            )
            db.session.add(note)
            db.session.commit()
            session.pop('title', None)
            session.pop('summarized_text', None)

            flash("Note saved successfully!", "success")
            return redirect(url_for('notes'))

        if form.validate_on_submit():
            if form.type.data == 'Summarize':
                if 'preview' in request.form:
                    uploaded_file = form.file.data
                    if uploaded_file:
                        filename = secure_filename(uploaded_file.filename)
                        save_path = os.path.join("uploads", filename)
                        uploaded_file.save(save_path)

                        text = extract_text(save_path)
                        print(type(text))
                        summarized_text = summarize_text(text)

                        os.remove(save_path)

                        session['title'] = form.title.data
                        session['summarized_text'] = summarized_text

                        return render_template(
                            'preview_ai_notes.html',
                            title=form.title.data,
                            content=summarized_text
                        )
                
    return render_template('create_ai_notes.html', form=form)

@app.route('/notes')
@login_required
def notes():
    page = request.args.get('page', 1, type=int)
    notes = Notes.query.filter_by(owner_id=current_user.id).order_by(Notes.date_created.desc()).paginate(page=page, per_page=10)
    return render_template('notes.html', notes=notes)

@app.route('/quizzes', methods=["GET", "POST"])
@login_required
def quizzes():
    form = CreateQuizForm()
    notes = Notes.query.filter_by(owner_id=current_user.id).all()
    quizzes =  Quiz.query.filter_by(owner_id=current_user.id).all()
    
    form.note.choices = [(note.id, note.title) for note in notes]

    if form.validate_on_submit():
        note_id = form.note.data
        model = form.model.data
        if model == 'Groq':
            return redirect(url_for('create_quiz', note_id=note_id))
        else:
            flash("Unsupported model selected", "danger")

    return render_template("quizzes.html", form=form, notes=notes, quizzes=quizzes)

@app.route('/create_quiz/<int:note_id>', methods=['GET', 'POST'])
@login_required
def create_quiz(note_id):
    note = Notes.query.get_or_404(note_id)
    if not note or note.author != current_user:
        abort(403)
    questions = generate_questions_using_groq(note.content)
    if isinstance(questions, dict) and "error" in questions:
        flash(questions["error"], "danger")
        return redirect(url_for("notes"))
    if request.method == 'POST':
        quiz = Quiz(
            owner_id=current_user.id,
            note_id=note.id,
            title=note.title,
            questions_json=dumps(questions),
        )
        db.session.add(quiz)
        db.session.commit()
        return redirect(url_for('quizzes'))
    return render_template('create_quiz_preview.html', questions=questions)

    