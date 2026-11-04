"""Additive, repeatable SQLite migration. Existing users and bookings are retained."""
from pathlib import Path
import sqlite3
from sqlalchemy import inspect, text

def upgrade(db):
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    additions = {
        'user': {'is_admin': 'BOOLEAN NOT NULL DEFAULT 0', 'created_at': 'DATETIME', 'interests': "TEXT DEFAULT ''", 'photo': 'VARCHAR(150)'},
        'professional': {'user_id': 'INTEGER REFERENCES user(id)', 'status': "VARCHAR(30) DEFAULT 'pending'", 'summary': 'TEXT', 'urgency': "VARCHAR(30) DEFAULT 'normal'"},
    }
    pending = [(table, field, spec) for table, fields in additions.items() if table in tables for field, spec in fields.items() if field not in {c['name'] for c in inspector.get_columns(table)}]
    if pending and db.engine.url.get_backend_name() == 'sqlite':
        path = Path(db.engine.url.database)
        backup = path.with_suffix('.pre-upgrade.db')
        if path.exists() and not backup.exists():
            with sqlite3.connect(path) as source, sqlite3.connect(backup) as target:
                source.backup(target)
    with db.engine.begin() as conn:
        for table, field, spec in pending:
            conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{field}" {spec}'))
    db.create_all()
