from app import create_app
from app.services.auth_service import auth_bp
from flask import Blueprint

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
