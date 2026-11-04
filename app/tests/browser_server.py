"""Disposable localhost-only browser fixture. Never opens the real users.db."""
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

if __name__ == '__main__':
    with TemporaryDirectory(prefix='career-guru-ui-') as directory:
        os.environ['DATABASE_URL'] = 'sqlite:///' + (Path(directory)/'verification.db').as_posix()
        os.environ['SECRET_KEY'] = 'disposable-browser-fixture-secret'
        os.environ['OLLAMA_MODEL'] = ''
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
        from app import app, db, bcrypt, User
        from seed import seed
        with app.app_context():
            db.create_all()
            seed()
            for name, admin in [('demo.student',False),('demo.admin',True)]:
                db.session.add(User(username=name,email=name+'@example.test',first_name='Asha' if not admin else 'Admin',password=bcrypt.generate_password_hash('verification-only-password').decode(),is_admin=admin))
            db.session.commit()
        app.run(host='127.0.0.1',port=5002,debug=False)
