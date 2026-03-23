# routes/main.py
from flask import Blueprint, render_template, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/debug')
def home():
    return {
        'message': 'Hello, World!',
        'status': 'running',
        'version': '1.0.0'
    }

@main_bp.route('/')
def html_page():
    return render_template('index.html')
