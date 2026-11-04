import os
import sqlite3
import subprocess
import sys
from pathlib import Path

def test_additive_migration_preserves_legacy_rows_and_edits(tmp_path):
    path=tmp_path/'legacy.db'
    with sqlite3.connect(path) as connection:
        connection.executescript('''
        CREATE TABLE user (id INTEGER PRIMARY KEY, username VARCHAR(100) UNIQUE NOT NULL, email VARCHAR(100) UNIQUE NOT NULL, password VARCHAR(100) NOT NULL, first_name VARCHAR(50), last_name VARCHAR(50), age INTEGER, location VARCHAR(100), phone_number VARCHAR(20), birthday DATE);
        CREATE TABLE professional (id INTEGER PRIMARY KEY, name VARCHAR(100) NOT NULL, email VARCHAR(100) NOT NULL, phone VARCHAR(20) NOT NULL, occupation VARCHAR(100) NOT NULL, industry VARCHAR(100) NOT NULL, company VARCHAR(100) NOT NULL, area_of_interest VARCHAR(100) NOT NULL, current_challenges TEXT NOT NULL, desired_outcome TEXT NOT NULL, availability VARCHAR(100) NOT NULL, additional_comments TEXT NOT NULL, timestamp DATETIME);
        INSERT INTO user VALUES (1,'legacy','legacy@example.test','preserve-original-hash','Legacy',NULL,20,'Test city','123',NULL);
        INSERT INTO professional VALUES (1,'Legacy','legacy@example.test','123','Student','Engineering','','Study','Next step','Guidance','Saturday','','2024-01-01 00:00:00');
        ''')
    environment={**os.environ,'DATABASE_URL':'sqlite:///'+path.as_posix(),'OLLAMA_MODEL':''}
    root=Path(__file__).resolve().parents[1]
    def initialize():
        result=subprocess.run([sys.executable,'-m','flask','--app','app','init-db'],cwd=root,env=environment,capture_output=True,text=True,timeout=60)
        assert result.returncode==0,result.stderr
    initialize()
    assert path.with_suffix('.pre-upgrade.db').exists()
    with sqlite3.connect(path) as connection:
        assert connection.execute('SELECT username,password,is_admin FROM user').fetchone()==('legacy','preserve-original-hash',0)
        assert connection.execute('SELECT name,availability,user_id FROM professional').fetchone()==('Legacy','Saturday',None)
        count=connection.execute('SELECT count(*) FROM career').fetchone()[0]
        connection.execute("UPDATE career SET title='Edited after migration' WHERE id=1")
    initialize()
    with sqlite3.connect(path) as connection:
        assert connection.execute('SELECT title FROM career WHERE id=1').fetchone()[0]=='Edited after migration'
        assert connection.execute('SELECT count(*) FROM career').fetchone()[0]==count
