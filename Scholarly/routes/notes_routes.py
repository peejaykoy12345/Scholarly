import os
from flask import Blueprint, render_template, flash, redirect, request, url_for, session, abort
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from Scholarly import db
from Scholarly.models import Notes
from Scholarly.forms import CreateNoteForm, CreateAINotes
from Scholarly.routes.AI.text_extracter import extract_text
from Scholarly.routes.AI.summarize import summarize_text

notes_bp = Blueprint("notes", __name__)

@notes_bp.route('/manually_create_notes', methods=["GET", "POST"])
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
        return redirect(url_for('notes.notes'))
    return render_template('manually_create_notes.html', form=form)

@notes_bp.route('/create_ai_notes', methods=['GET', 'POST'])
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
            return redirect(url_for('notes.notes'))

        if form.validate_on_submit():
            if form.type.data == 'Summarize':
                if 'preview' in request.form:
                    uploaded_file = form.file.data
                    if uploaded_file:
                        os.makedirs("uploads", exist_ok=True)
                        filename = secure_filename(uploaded_file.filename)
                        save_path = os.path.join("uploads", filename)
                        uploaded_file.save(save_path)

                        text = extract_text(save_path)
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

@notes_bp.route('/notes')
@login_required
def notes():
    page = request.args.get('page', 1, type=int)
    notes = Notes.query.filter_by(owner_id=current_user.id).order_by(Notes.date_created.desc()).paginate(page=page, per_page=10)
    return render_template('notes.html', notes=notes)

@notes_bp.route('/view_notes/<int:note_id>')
@login_required
def view_notes(note_id):
    note = Notes.query.get_or_404(note_id)
    
    if note.owner_id != current_user.id:
        abort(403)

    return render_template('view_notes.html', note=note)