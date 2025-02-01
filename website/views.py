from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime  # Added for timestamp
from .models import Note, Post, Comment, db
from .forms import NoteForm, PostForm, CommentForm

# Define constants
UPLOAD_FOLDER = 'website/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB (New constant for file size limit)

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

views = Blueprint('views', __name__)

# Home route - Display posts and notes
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.date.desc()).all()

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

    return render_template("home.html", user=current_user, posts=posts, notes=notes)

# Create post route (with all 3 improvements)
@views.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        # Check file size before processing
        if request.content_length > MAX_FILE_SIZE:
            flash('File size exceeds the limit (5MB).', 'error')
            return redirect(url_for('views.create_post'))

        title = form.title.data
        content = form.content.data
        image = form.image.data
        image_path = None

        # Handle image upload
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(file_path)
            image_path = filename

        # Create post with explicit timestamp
        new_post = Post(
            title=title,
            content=content,
            image_path=image_path,
            user_id=current_user.id,
            timestamp=datetime.utcnow()  # Explicit timestamp
        )

        # Error handling for database operations
        try:
            db.session.add(new_post)
            db.session.commit()
            flash('Post created successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the post.', 'error')
        
        return redirect(url_for('views.home'))

    return render_template('create_post.html', form=form, user=current_user)

# Upload route (updated with file size check)
@views.route('/upload', methods=['POST'])
@login_required
def upload():
    # File size check
    if request.content_length > MAX_FILE_SIZE:
        return jsonify({'success': False, 'message': 'File size exceeds the limit (5MB).'})

    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected.'})

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected.'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        try:
            file.save(file_path)
        except Exception as e:
            print(f"Error saving file: {e}")
            return jsonify({'success': False, 'message': 'Error saving file.'})

        try:
            new_note = Note(
                data=f"Image uploaded: {filename}", 
                user_id=current_user.id, 
                image_path=filename
            )
            db.session.add(new_note)
            db.session.commit()
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
            print(f"Database error: {e}")
            return jsonify({'success': False, 'message': 'Database error.'})
    else:
        return jsonify({'success': False, 'message': 'Invalid file type.'})

@views.route('/profile')
@login_required
def profile():
    # Get all posts by the current user, ordered by timestamp
    user_posts = Post.query.filter_by(user_id=current_user.id)\
                          .order_by(Post.timestamp.desc())\
                          .all()
    return render_template("profile.html", user=current_user, posts=user_posts)
