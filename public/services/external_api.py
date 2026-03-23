# services/external_api.py
import requests
import os
from flask import current_app

class ExternalAPIService:
    def __init__(self):
        self.api_key = os.environ.get('API_KEY')
        self.base_url = os.environ.get('API_BASE_URL', 'https://api.github.com')
    
    def get_data(self):
        """Example: Fetch data from GitHub API"""
        try:
            response = requests.get(f'{self.base_url}/users/octocat')
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status': 'failed'}, 500
    
    def post_data(self, endpoint, data):
        """Generic POST method for external APIs"""
        headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
        
        try:
            response = requests.post(
                f'{self.base_url}/{endpoint}',
                json=data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
