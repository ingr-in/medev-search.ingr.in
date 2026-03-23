import os
from flask import Flask
from routes.main import main
from routes.api import api

app = Flask(__name__)

# Register routes
app.register_blueprint(main)
app.register_blueprint(api, url_prefix="/api")

if __name__ == '__main__':
    app.run(host='https://python.ingr.in/')
