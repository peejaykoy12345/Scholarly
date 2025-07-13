import secrets, os
from flask import render_template, flash, redirect, request, url_for, session, abort
from flask_login import current_user, login_required, logout_user, login_user
from Scholarly import app, db, bcrypt
from Scholarly.models import User, Notes, Quiz, QuizResult
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

@app.route('/view_notes/<int:note_id>')
@login_required
def view_notes(note_id):
    note = Notes.query.get_or_404(note_id)
    
    if note.owner_id != current_user.id:
        abort(403)

    return render_template('view_notes.html', note=note)

@app.route('/quizzes', methods=["GET", "POST"])
@login_required
def quizzes():
    form = CreateQuizForm()
    notes = Notes.query.filter_by(owner_id=current_user.id).order_by(Notes.date_created.desc()).all()
    quizzes = Quiz.query.filter_by(owner_id=current_user.id).order_by(Quiz.date_created.desc()).all()
    form.note.choices = [(note.id, note.title) for note in notes]

    if request.method == "POST" and request.form.get("confirm_quiz"):
        print("RANN")
        try:
            questions = session.get("quiz_questions")
            note_id = session.get("quiz_note_id")

            print(questions, " is questions from sesssion")

            if not questions or not note_id:
                flash("Session expired. Please generate the quiz again.", "danger")
                return redirect(url_for("quizzes"))

            note = Notes.query.get_or_404(note_id)

            quiz = Quiz(
                owner_id=current_user.id,
                note_id=note.id,
                title=note.title,
                model_used="Groq",  
                quiz_type="Multiple Choice",
                questions_json=dumps({"output": questions})
            )
            db.session.add(quiz)
            db.session.commit()

            session.pop("quiz_questions", None)
            session.pop("quiz_note_id", None)

            flash("✅ Quiz created successfully!", "success")
            return redirect(url_for('quizzes'))

        except Exception as e:
            flash(f"Something went wrong saving the quiz: {e}", "danger")
            return redirect(url_for('quizzes'))

    if form.validate_on_submit():
        note_id = form.note.data
        model = form.model.data
        quiz_type = form.quiz_type.data
        question_count = form.question_count.data

        note = Notes.query.get_or_404(note_id)
        if note.owner_id != current_user.id:
            abort(403)

        if model != "Groq":
            flash("Unsupported model selected", "danger")
            return redirect(url_for("quizzes"))

        questions = generate_questions_using_groq(note.content, quiz_type, question_count)

        print(questions, 'is questions from form.validate_on_submit')

        if isinstance(questions, dict) and "error" in questions:
            flash(questions["error"], "danger")
            return redirect(url_for("quizzes"))
        
        if isinstance(questions, dict) and "output" in questions:
            questions = questions["output"]

        print(questions, "is the formatted question")
        
        session["quiz_questions"] = questions
        session["quiz_note_id"] = note.id

        return render_template("create_quiz_preview.html", questions=questions, note=note)

    return render_template("quizzes.html", form=form, notes=notes, quizzes=quizzes)

@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if quiz.owner_id != current_user.id:
        print(quiz.ownenr_id, " | ", current_user.id)
        abort(403)

    QuizResult.query.filter_by(quiz_id=quiz.id).delete()
    db.session.delete(quiz)
    db.session.commit()
    flash('✅ Quiz successfully deleted!', 'success')
    return redirect(url_for('quizzes'))

@app.route('/view_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if not quiz or quiz.author != current_user:
        abort(403)
    
    questions_data = quiz.get_questions()
    print(questions_data, " is question data")
    questions = questions_data["output"] if isinstance(questions_data, dict) else questions_data
    
    print(type(questions), "is question type")
    print(questions, "is questions")

    if request.method == 'POST':
        QuizResult.query.filter_by(quiz_id=quiz_id).delete()
        question_counter = 0
        
        for question in questions:
            form_key = f"answer_{question_counter}"
            selected = request.form.get(form_key)
            
            selected_index = int(selected) if selected else -1
            correct_index = question["answer_index"]
            
            result = QuizResult(
                user_id=current_user.id,
                quiz_id=quiz.id,
                question=question["question"],
                correct_answer=question["choices"][correct_index],
                user_answer=question["choices"][selected_index] if 0 <= selected_index < len(question["choices"]) else "N/A",
                explanation=question.get("explanation", "No explanation provided"),
                is_correct=(selected_index == correct_index)
            )
            print(
                f"User: {current_user.id}, "
                f"Quiz: {quiz.id}, "
                f"Q: {question['question']}, "
                f"Correct: {question['choices'][correct_index]}, "
                f"Selected: {question['choices'][selected_index] if 0 <= selected_index < len(question['choices']) else 'N/A'}, "
                f"Correct?: {'✅' if selected_index == correct_index else '❌'}"
            )
            db.session.add(result)
            question_counter += 1
        
        db.session.commit()
        return redirect(url_for('quizzes'))
    
    return render_template('view_quiz.html', quiz=quiz, questions=questions)

@app.route('/view_results/<int:quiz_id>')
@login_required
def view_results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.owner_id != current_user.id:
        abort(403)
    return render_template('view_results.html', results=quiz.results, quiz=quiz)
    
