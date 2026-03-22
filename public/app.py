# app.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World! This is my Python app on Render!'

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='https://python.ingr.in/')
