from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
from .models import Note, db
from .forms import NoteForm

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = 'website/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')
        
        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            try:
                new_note = Note(data=note, user_id=current_user.id)
                db.session.add(new_note)
                db.session.commit()
                flash('Note added!', category='success')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while adding the note.', category='error')
    return render_template("home.html", user=current_user)

@views.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected.'})

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected.'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        try:
            # Save the file to the upload folder
            file.save(file_path)
        except Exception as e:
            print(f"Error saving file: {e}")  # Log the error for debugging
            return jsonify({'success': False, 'message': 'An error occurred while saving the file.'})

        try:
            # Save the image path to the database
            new_note = Note(data=f"Image uploaded: {filename}", user_id=current_user.id, image_path=filename)
            db.session.add(new_note)
            db.session.commit()

            # Return the new note's data as JSON
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully.',
                'note': {
                    'id': new_note.id,
                    'data': new_note.data,
                    'image_path': new_note.image_path
                }
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error saving note to database: {e}")  # Log the error for debugging
            return jsonify({'success': False, 'message': f'An error occurred while saving the note: {str(e)}'})
    else:
        return jsonify({'success': False, 'message': 'Invalid file type. Allowed types are: png, jpg, jpeg, gif.'})

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            try:
                db.session.delete(note)
                db.session.commit()
                flash('Note deleted successfully!', category='success')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while deleting the note.', category='error')
    return jsonify({})