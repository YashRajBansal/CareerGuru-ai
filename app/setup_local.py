"""Create local configuration without displaying secrets or overwriting credentials."""
from pathlib import Path
import secrets
from dotenv import dotenv_values, set_key

root = Path(__file__).resolve().parent
target = root / '.env'
if not target.exists():
    target.write_text((root / '.env.example').read_text(encoding='utf-8-sig'), encoding='utf-8')
if not dotenv_values(target).get('SECRET_KEY'):
    set_key(str(target), 'SECRET_KEY', secrets.token_urlsafe(48))
print('Local configuration ready. Add new API and mail credentials to app/.env when needed.')
