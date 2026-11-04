"""Safe development entry point. Never deletes application records."""
from app import app

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
