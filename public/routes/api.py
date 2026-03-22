# routes/api.py
from flask import Blueprint, request, jsonify
import requests

api_bp = Blueprint('api', __name__)

@api_bp.route('/data', methods=['GET'])
def get_data():
    """Example API endpoint"""
    return jsonify({
        'data': 'Your data here',
        'method': 'GET'
    })

@api_bp.route('/data', methods=['POST'])
def post_data():
    """Example POST endpoint"""
    data = request.get_json()
    # Process data
    return jsonify({'received': data, 'status': 'success'}), 201
