import os
from flask import Flask
from man.main import main
from man.api import api
from man.bots import bots

app = Flask(__name__)

# Register routes
app.register_blueprint(main)
app.register_blueprint(api")
app.register_blueprint(bots)

if __name__ == '__main__':
    app.run(host='https://python.ingr.in/')
