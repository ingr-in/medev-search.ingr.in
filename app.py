import os
from flask import Flask, render_template
from spy.man.health import health
from spy.man.main import main
from spy.man.api import api
from spy.man.bots import bots

app = Flask(
    __name__,
    template_folder="spy/templates",
    static_folder="spy/static"
)

# Blueprints Register
app.register_blueprint(main)
app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(bots, url_prefix="/bots")
app.register_blueprint(health)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/spy")
def spy():
    return {
        "message": "spy working"
    }

if __name__ == "__main__":
    app.run(debug=True)
