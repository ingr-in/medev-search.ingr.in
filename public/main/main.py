from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/debug')
def debug():
    return {
        'message': 'Hello, World!',
        'status': 'running',
        'version': '1.0.0'
    }

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')
