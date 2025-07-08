import secrets, os
from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_required, logout_user, login_user
from Scholarly import app, db, bcrypt
from Scholarly.models import User, Notes
from Scholarly.forms import LoginForm, RegistrationForm, AccountForm, CreateNoteForm, CreateAINotes
from PIL import Image
from werkzeug.utils import secure_filename
from AI.text_extracter import extract_text
from AI.summarize import summarize_text

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
            title=form.title.data,
            content=form.content.data
        )
        db.session.add(note)
        db.session.commit()
        flash("Your note has been created!", 'success')
        return redirect(url_for('notes'))
    return render_template('manually_create_notes.html')

@app.route('/create_ai_notes', methods=['GET', 'POST'])
@login_required
def create_ai_notes():
    form = CreateAINotes()
    if request.method == 'POST':
        if form.type.data == 'Summarize':
            uploaded_file = form.file.data
            if uploaded_file:
                filename = secure_filename(uploaded_file.filename)

                save_path = os.path.join("uploads", filename)
                uploaded_file.save(save_path)
                
                text = extract_text(save_path)

                summarized_text = summarize_text(text)

                os.remove(save_path)

                note = Notes(
                    title=form.title.data,
                    content=summarized_text
                )

                db.session.add(note)
                db.session.commit()

                
    return render_template('create_ai_notes.html')

@app.route('/notes')
@login_required
def notes():
    page = request.args.get('page', 1, type=int)
    notes = Notes.query.filter_by(owner_id=current_user.id).order_by(Notes.date_created.desc()).paginate(page=page, per_page=10)
    return render_template('notes.html', notes=notes)