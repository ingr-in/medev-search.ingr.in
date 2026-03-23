from flask import Flask
from routes.main import main_routes
from routes.api import api_routes

app = Flask(__name__)

# Register routes
app.register_blueprint(main_routes)
app.register_blueprint(api_routes, url_prefix="/api")

if __name__ == '__main__':
    app.run(host='https://python.ingr.in/')
