import os
from flask import Flask
from spy.man.main import main
from spy.man.api import api
from spy.man.bots import bots
from flask import Flask, render_template

app = Flask(
    __name__,
    template="spy/templates",
    static="spy/static",
    main="spy/main/",
    api="spy/api",
    bots="spy/bots"
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/spy")
def spy():
    return {
        "message": "pydir working"
    }

if __name__ == "__main__":
    app.run(debug=True)
