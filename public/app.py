# app.py
from flask import Flask, render_template, jsonify, request
import logging
import traceback

app = Flask(__name__)

# Register error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 - Page Not Found"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Resource not found'}), 404
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 - Forbidden"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Access denied'}), 403
    return render_template('errors/403.html'), 403

@app.errorhandler(400)
def bad_request_error(error):
    """Handle 400 - Bad Request"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Bad request'}), 400
    return render_template('errors/400.html'), 400

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 - Internal Server Error"""
    # Log the error for debugging
    app.logger.error(f'Server Error: {error}')
    app.logger.error(traceback.format_exc())
    
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('errors/500.html'), 500

@app.errorhandler(429)
def too_many_requests_error(error):
    """Handle 429 - Too Many Requests"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Too many requests'}), 429
    return render_template('errors/429.html'), 429

# Custom error handler for all unhandled exceptions
@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all unhandled exceptions"""
    app.logger.error(f'Unhandled Exception: {error}')
    app.logger.error(traceback.format_exc())
    
    if request.path.startswith('/api/'):
        return jsonify({'error': 'An unexpected error occurred'}), 500
    return render_template('errors/500.html'), 500

# Your regular routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Example route that might cause errors
@app.route('/user/<int:user_id>')
def get_user(user_id):
    if user_id < 1:
        # This will trigger 404 handler
        abort(404)
    
    # Simulate database error
    if user_id == 999:
        raise Exception("Database connection failed")
    
    return jsonify({'user_id': user_id})

# Import abort for route examples
from werkzeug.exceptions import abort

if __name__ == '__main__':
    app.run(host='https://python.ingr.in/')
