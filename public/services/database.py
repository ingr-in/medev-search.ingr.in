# services/database.py
import os
import sqlite3
from flask import g, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Initialize SQLAlchemy (for ORM approach)
db = SQLAlchemy()

# For raw SQL approach
def get_db():
    """Get database connection for raw SQL"""
    if 'db' not in g:
        # Use SQLite for development, PostgreSQL for production
        database_url = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
        
        if database_url.startswith('postgres'):
            import psycopg2
            g.db = psycopg2.connect(database_url)
        else:
            # Remove sqlite:/// prefix for SQLite
            db_path = database_url.replace('sqlite:///', '')
            g.db = sqlite3.connect(db_path)
            g.db.row_factory = sqlite3.Row
        
    return g.db

def init_db(app):
    """Initialize database with tables"""
    with app.app_context():
        db = get_db()
        
        # Create tables
        if isinstance(db, sqlite3.Connection):
            cursor = db.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Posts table example
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            db.commit()
            print("Database initialized successfully!")
        
        elif 'psycopg2' in str(type(db)):
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT,
                    user_id INTEGER REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            db.commit()
            print("PostgreSQL database initialized successfully!")

def close_db(error=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# For SQLAlchemy ORM approach (more advanced)
def init_sqlalchemy(app):
    """Initialize SQLAlchemy with app"""
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///app.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        print("SQLAlchemy database initialized!")

# Models for SQLAlchemy
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    posts = db.relationship('Post', backref='author', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
