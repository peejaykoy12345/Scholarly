from flask import Blueprint, render_template, url_for, redirect, abort, request, session, flash
from flask_login import current_user, login_required
from json import dumps
from Scholarly import db
from Scholarly.models import Notes, Flashcards
from Scholarly.forms import CreateFlashCardsForm, DeleteButton
from Scholarly.routes.AI.learn.flashcards import generate_flashcards

learn_bp = Blueprint("learn", __name__, url_prefix="/learn")

@learn_bp.route("/")
def home():
    return render_template("learn/home.html")

@learn_bp.route('/flashcards', methods=['GET', 'POST'])
@login_required
def flashcards():
    page = request.args.get('page', 1, type=int)
    flashcards = Flashcards.query.filter_by(user_id=current_user.id).order_by(Flashcards.date_created.desc()).paginate(page=page, per_page=10)
    notes = Notes.query.filter_by(owner_id=current_user.id).order_by(Notes.date_created.desc()).all()

    flashcards_form = CreateFlashCardsForm()
    flashcards_form.note.choices = [(note.id, note.title) for note in notes]

    delete_button = DeleteButton()

    if flashcards_form.validate_on_submit():
        note_id = flashcards_form.note.data
        model = flashcards_form.model.data
        flashcards_count = flashcards_form.flashcards_count.data
    
        note = Notes.query.get_or_404(note_id)
        if note.author != current_user:
            abort(403)

        flashcards_json = generate_flashcards(note.content, flashcards_count)

        if isinstance(flashcards_json, dict) and "error" in flashcards_json:
            flash(flashcards_json["error"], "danger")
            return redirect(url_for("quiz.quizzes"))

        if isinstance(flashcards_json, dict) and "output" in flashcards_json:
            flashcards_json = flashcards_json["output"]

        session["flashcards_preview"] = {
            "flashcards_json": flashcards_json,
            "title": note.title,
            "note_id": note.id,
            "model": model,
        }

        return render_template("learn/flashcards_preview.html", flashcards=session["flashcards_preview"])
    
    elif request.method == "POST" and "flashcards_preview" in session:
        new_flashcards = Flashcards(
            user_id = current_user.id,
            note_id = session["flashcards_preview"]["note_id"],
            title = session["flashcards_preview"]["title"],
            flashcards_json = dumps({"output": session["flashcards_preview"]["flashcards_json"]})
        )
        db.session.add(new_flashcards)
        db.session.commit()
        session.pop("flashcards_preview", None)
        flash("Flashcards successfully created!", "success")
        return redirect(url_for('learn.flashcards'))

    elif request.method == "POST":
        flash("Session expired", "danger")
        return redirect(url_for('learn.flashcards'))

    return render_template('learn/flashcards.html', flashcards_form=flashcards_form, flashcards=flashcards, delete_button=delete_button)

@learn_bp.route('/view_flashcards/<int:flashcard_id>')
@login_required
def view_flashcards(flashcard_id):
    flashcard = Flashcards.query.get_or_404(flashcard_id)

    if flashcard.author != current_user:
        abort(403)

    flashcards = flashcard.get_flashcards()
    
    return render_template('learn/view_flashcards.html', flashcards=flashcards)


@learn_bp.route('/delete_flashcards/<int:flashcard_id>', methods=["POST"])
@login_required
def delete_flashcards(flashcard_id):
    flashcard = Flashcards.query.get_or_404(flashcard_id)

    if flashcard.author != current_user:
        abort(403)

    db.session.delete(flashcard)
    db.session.commit()

    flash("Flashcard deleted!", "success")
    return redirect(url_for("learn.flashcards"))