"""Career Guru configuration, preserved models, and secure application setup."""
import os
from pathlib import Path
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')

def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

app = Flask(__name__)
if not os.getenv('SECRET_KEY'):
    raise RuntimeError('Set SECRET_KEY in app/.env before starting Career Guru.')
app.config.update(
    SECRET_KEY=os.environ['SECRET_KEY'],
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///users.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.getenv('COOKIE_SECURE', 'false').lower() == 'true',
    MAX_CONTENT_LENGTH=4 * 1024 * 1024,
    MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', '587')), MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'), MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER') or os.getenv('MAIL_USERNAME'),
)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
csrf = CSRFProtect(app)
limiter = Limiter(get_remote_address, app=app, storage_uri=os.getenv('RATELIMIT_STORAGE_URI', 'memory://'), default_limits=['300 per hour'])
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    location = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    birthday = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=now)
    interests = db.Column(db.Text, default='')
    photo = db.Column(db.String(150))

class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    occupation = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    area_of_interest = db.Column(db.String(100), nullable=False)
    current_challenges = db.Column(db.Text, nullable=False)
    desired_outcome = db.Column(db.Text, nullable=False)
    availability = db.Column(db.String(100), nullable=False)
    additional_comments = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(30), default='pending')
    summary = db.Column(db.Text)
    urgency = db.Column(db.String(30), default='normal')

class Career(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    cluster = db.Column(db.String(100), nullable=False)
    skills = db.Column(db.Text, nullable=False)
    traits = db.Column(db.Text, nullable=False)
    education = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    outlook = db.Column(db.Text, nullable=False)
    source = db.Column(db.Text, default='Editorial career exploration profile; verify local entry requirements.')
    embedding = db.Column(db.JSON)
    embedding_model = db.Column(db.String(100))
    position = db.Column(db.Integer, default=0)
    def document(self):
        return f'{self.title}. {self.cluster}. Skills: {self.skills}. Interests: {self.traits}. {self.description}. Education: {self.education}. Outlook: {self.outlook}'
    def public(self):
        return {k: getattr(self, k) for k in ('id', 'title', 'cluster', 'skills', 'traits', 'education', 'description', 'outlook', 'source')}

class Knowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    content = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.JSON)
    embedding_model = db.Column(db.String(100))
    def document(self):
        return f'{self.title}: {self.content}'

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(100), default='New conversation')
    kind = db.Column(db.String(20), default='counselor')
    created_at = db.Column(db.DateTime, default=now)
    messages = db.relationship('ChatMessage', cascade='all, delete-orphan', backref='conversation', order_by='ChatMessage.id')

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=now)

class ReviewQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question = db.Column('query', db.Text, nullable=False)
    reason = db.Column(db.String(100))
    resolved = db.Column(db.Boolean, default=False)
    resolution = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=now)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answers = db.Column(db.JSON, nullable=False)
    scores = db.Column(db.JSON, nullable=False)
    profile = db.Column(db.Text, nullable=False)
    interpretation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=now)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(150))
    result = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=now)

class SavedCareer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    career_id = db.Column(db.Integer, db.ForeignKey('career.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'career_id'),)

class CareerView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey('career.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=now)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime, default=now)

class CatalogRevision(db.Model):
    name = db.Column(db.String(100), primary_key=True)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id)) if user_id.isdigit() else None

@app.context_processor
def shared():
    from services.ai import configured
    return {'ai_ready': configured(), 'year': now().year}

@app.after_request
def headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    if current_user.is_authenticated:
        response.headers['Cache-Control'] = 'no-store'
    return response

@app.errorhandler(CSRFError)
def csrf_error(error):
    if request.path.startswith('/api/'):
        return jsonify(error='Your session expired. Reload the page and try again.'), 400
    return render_template('error.html', code=400, message='Your form expired. Reload the page and try again.'), 400

@app.errorhandler(404)
@app.errorhandler(403)
@app.errorhandler(413)
@app.errorhandler(429)
@app.errorhandler(405)
@app.errorhandler(500)
def error_page(error):
    message = {403: 'This workspace is restricted to administrators.', 404: 'We could not find that page.', 405: 'Use the page controls to perform this action.', 413: 'This file is too large. Please use a file under 4 MB.', 429: 'You are moving quickly. Please wait before trying again.', 500: 'Something interrupted your request. Please try again.'}.get(error.code, error.description)
    if request.path.startswith('/api/'):
        return jsonify(error=message), error.code
    return render_template('error.html', code=error.code, message=message), error.code

# Import routes after models, preserving app.py as the existing entry point.
import sys
if __name__ == '__main__':
    sys.modules['app'] = sys.modules[__name__]
from routes import register_routes
register_routes(app)

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=False)
