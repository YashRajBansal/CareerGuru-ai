import os
import sys
from pathlib import Path
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SECRET_KEY'] = 'test-only-session-secret'
os.environ['OLLAMA_MODEL'] = ''
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from app import app, db, bcrypt, limiter, User
from seed import seed

@pytest.fixture(autouse=True)
def database(monkeypatch):
    monkeypatch.setenv('OLLAMA_MODEL', '')
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=True)
    limiter.enabled = False
    with app.app_context():
        db.create_all()
        seed()
        for name, admin in [('student', False), ('other', False), ('staff', True)]:
            db.session.add(User(username=name, email=name+'@example.test', password=bcrypt.generate_password_hash('test-password-123').decode(), is_admin=admin))
        db.session.commit()
        yield
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client():
    return app.test_client()
