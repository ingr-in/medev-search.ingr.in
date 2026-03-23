# app.py
from flask import Flask
from config import Config
from routes.main import main_bp
from routes.api import api_bp
from services.database import init_db
from services.external_api import ExternalAPIService

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
init_db(app)

# Register blueprints (routes)
app.register_blueprint(main_bp)
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def home():
    return render_template('index.html')
    
# Health check
@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

# Example external API integration
@app.route('/external-data')
def external_data():
    external_service = ExternalAPIService()
    data = external_service.get_data()
    return data

if __name__ == '__main__':
    app.run(host='https://python.ingr.in/')
