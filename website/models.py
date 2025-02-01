from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))  # New field
    bio = db.Column(db.Text)  # New field
    profile_pic = db.Column(db.String(200))  # New field
    notes = db.relationship('Note', backref='user', lazy=True)  # Relationship to Note
    posts = db.relationship('Post', backref='author', lazy=True)  # Relationship to Post
    comments = db.relationship('Comment', backref='user', lazy=True)  # Relationship to Comment

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    image_path = db.Column(db.String(200), nullable=True)  # Optional image upload
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Foreign key to User

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200), nullable=True)  # Optional image upload
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for post
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Foreign key to User
    comments = db.relationship('Comment', backref='post', lazy=True)  # Relationship to Comment
   

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for comment
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Foreign key to User
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))  # Foreign key to Post