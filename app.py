import os
from flask import Flask
from spy.man.main import main
from spy.man.api import api
from spy.man.bots import bots

app = Flask(__name__)

# Register routes
app.register_blueprint(main)
app.register_blueprint(api,url_prefix="/api")
app.register_blueprint(bots,url_prefix="/api")

if __name__ == '__main__':
    app.run(host='https://python.ingr.in/')
