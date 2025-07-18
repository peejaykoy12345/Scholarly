from flask import Blueprint, render_template, abort
from flask_login import current_user, login_required
from Scholarly.models import Notes
from Scholarly.forms import CreateFlashCardsForm
from Scholarly.routes.AI.learn.flashcards import generate_flashcards

learn_bp = Blueprint("learn", __name__, url_prefix="/learn")

@learn_bp.route('/', methods=['GET', 'POST'])
def home():
    notes = Notes.query.filter_by(owner_id=current_user.id).order_by(Notes.date_created.desc()).all()

    flashcards_form = CreateFlashCardsForm()
    flashcards_form.note.choices = [(note.id, note.title) for note in notes]

    if flashcards_form.validate_on_submit():
        note_id = flashcards_form.note.data
        model = flashcards_form.model.data
        flashcards_count = flashcards_form.flashcards_count.data
    
        note = Notes.query.get_or_404(note_id)
        if note.author != current_user:
            abort(403)

    return render_template('learn/home.html')

@learn_bp.route('/flashcards')
@login_required
def flashcards():
    
    return render_template('learn/flashcards.html')