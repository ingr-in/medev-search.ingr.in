# utils/helpers.py
import json
from datetime import datetime

def format_response(data, status=200):
    """Format API response consistently"""
    return {
        'status': status,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }

def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
