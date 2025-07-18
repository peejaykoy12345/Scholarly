import os
from flask import Blueprint, render_template, flash, redirect, request, url_for, abort
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from Scholarly import db
from Scholarly.models import Notes
from Scholarly.forms import CreateNoteForm, CreateAINotes, CSRFButton
from Scholarly.routes.AI.text_extracter import extract_text
from Scholarly.routes.AI.notes_creator import generate_notes_using_ai as generate_notes

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
            title = request.form.get('title')
            content = request.form.get('generated_notes')

            if not title or not content:
                flash("Missing title or content during confirmation.", "danger")
                return redirect(url_for('notes.create_ai_notes'))

            note = Notes(
                title=title,
                content=content,
                owner_id=current_user.id
            )
            db.session.add(note)
            db.session.commit()
            flash("Note saved successfully!", "success")
            return redirect(url_for('notes.notes'))

        if form.validate_on_submit():
            if 'preview' in request.form:
                uploaded_file = form.file.data
                if uploaded_file:
                    os.makedirs("uploads", exist_ok=True)
                    filename = secure_filename(uploaded_file.filename)
                    save_path = os.path.join("uploads", filename)
                    uploaded_file.save(save_path)

                    text = extract_text(save_path)
                    generated_notes = generate_notes(text, form.type.data)

                    os.remove(save_path)

                    return render_template(
                        'preview_ai_notes.html',
                        title=form.title.data,
                        content=generated_notes,
                        form=form
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

@notes_bp.route('/delete_notes/<int:note_id>')
@login_required
def delete_notes(note_id):
    note = Notes.query.get_or_404(note_id)

    if note.author != current_user:
        abort(403)

    db.session.delete(note)
    db.session.commit()
    flash("Note successfully deleted", "success")

    return redirect(url_for('notes.notes'))
