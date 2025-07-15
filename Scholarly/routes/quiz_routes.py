import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from json import dumps
from Scholarly import db
from Scholarly.models import Notes, Quiz, QuizResult
from Scholarly.forms import CreateQuizForm
from Scholarly.routes.AI.quiz_gen.quiz_gen_groq import generate_questions_but_with_long_text as generate_questions_using_groq

quiz_bp = Blueprint("quiz", __name__)

@quiz_bp.route('/quizzes', methods=["GET", "POST"])
@login_required
def quizzes():
    form = CreateQuizForm()
    notes = Notes.query.filter_by(owner_id=current_user.id).order_by(Notes.date_created.desc()).all()
    quizzes = Quiz.query.filter_by(owner_id=current_user.id).order_by(Quiz.date_created.desc()).all()
    form.note.choices = [(note.id, note.title) for note in notes]

    if request.method == "POST" and request.form.get("confirm_quiz"):
        try:
            questions = session.get("quiz_questions")
            quiz_type = session.get('quiz_type')
            note_id = session.get("quiz_note_id")

            if not questions or not note_id or not quiz_type:
                flash("Session expired. Please generate the quiz again.", "danger")
                return redirect(url_for("quiz.quizzes"))

            note = Notes.query.get_or_404(note_id)

            quiz = Quiz(
                owner_id=current_user.id,
                note_id=note.id,
                title=note.title,
                model_used="Groq",
                quiz_type=quiz_type,
                questions_json=dumps({"output": questions})
            )
            db.session.add(quiz)
            db.session.commit()

            session.pop("quiz_questions", None)
            session.pop("quiz_note_id", None)
            session.pop("quiz_type", None)

            flash("✅ Quiz created successfully!", "success")
            return redirect(url_for("quiz.quizzes"))

        except Exception as e:
            flash(f"Something went wrong saving the quiz: {e}", "danger")
            return redirect(url_for("quiz.quizzes"))

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
            return redirect(url_for("quiz.quizzes"))

        questions = generate_questions_using_groq(note.content, quiz_type, question_count)

        if isinstance(questions, dict) and "error" in questions:
            flash(questions["error"], "danger")
            return redirect(url_for("quiz.quizzes"))

        if isinstance(questions, dict) and "output" in questions:
            questions = questions["output"]

        session["quiz_questions"] = questions
        session["quiz_note_id"] = note.id
        session["quiz_type"] = quiz_type

        return render_template("create_quiz_preview.html", questions=questions, note=note)

    return render_template("quizzes.html", form=form, notes=notes, quizzes=quizzes)


@quiz_bp.route('/quick_quiz', methods=['GET', 'POST'])
@login_required
def quick_quiz():
    form = CreateQuizForm()
    notes = Notes.query.filter_by(owner_id=current_user.id).order_by(Notes.date_created.desc()).all()
    form.note.choices = [(note.id, note.title) for note in notes]

    if form.validate_on_submit():
        note_id = form.note.data
        model = form.model.data
        quiz_type = form.quiz_type.data
        question_count = form.question_count.data

        note = Notes.query.get_or_404(note_id)
        if note.owner_id != current_user.id:
            abort(403)

        questions = generate_questions_using_groq(note.content, quiz_type, question_count)

        if isinstance(questions, dict) and "error" in questions:
            flash(questions["error"], "danger")
            return redirect(url_for("quiz.quizzes"))

        if isinstance(questions, dict) and "output" in questions:
            questions = questions["output"]

        session['temp_quiz'] = {
            "questions": questions,
            "title": note.title,
            "quiz_type": quiz_type,
            "model": model
        }

        return render_template('view_quiz.html', quiz=session['temp_quiz'], questions=questions)

    elif request.method == 'POST' and 'temp_quiz' in session:
        quiz_data = session['temp_quiz']
        questions = quiz_data['questions']
        results = []

        for i, question in enumerate(questions):
            selected = request.form.get(f"answer_{i}")
            selected_index = int(selected) if selected else -1
            correct_index = question["answer_index"]

            result = {
                "question": question["question"],
                "correct_answer": question["choices"][correct_index],
                "user_answer": question["choices"][selected_index] if 0 <= selected_index < len(question["choices"]) else "N/A",
                "explanation": question.get("explanation", "No explanation provided"),
                "is_correct": selected_index == correct_index
            }
            results.append(result)

        return render_template('view_results.html', results=results, quiz=quiz_data)

    return render_template('create_quick_quiz.html', form=form)


@quiz_bp.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if quiz.owner_id != current_user.id:
        abort(403)

    QuizResult.query.filter_by(quiz_id=quiz.id).delete()
    db.session.delete(quiz)
    db.session.commit()
    flash('✅ Quiz successfully deleted!', 'success')
    return redirect(url_for('quiz.quizzes'))


@quiz_bp.route('/view_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.owner_id != current_user.id:
        abort(403)

    questions_data = quiz.get_questions()
    questions = questions_data["output"] if isinstance(questions_data, dict) else questions

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
            db.session.add(result)
            question_counter += 1

        db.session.commit()
        return redirect(url_for('quiz.quizzes'))

    return render_template('view_quiz.html', quiz=quiz, questions=questions)


@quiz_bp.route('/view_results/<int:quiz_id>')
@login_required
def view_results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.owner_id != current_user.id:
        abort(403)
    return render_template('view_results.html', results=quiz.results, quiz=quiz)
