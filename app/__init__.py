from flask import Flask
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
from flask_cors import CORS
load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    if not app.config["JWT_SECRET_KEY"]:
        raise RuntimeError("JWT_SECRET_KEY not set")

    JWTManager(app)
    CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:3000",
                "http://127.0.0.1:3000"
            ]
        }
    },
    supports_credentials=True, 
    allow_headers=["Authorization", "Content-Type"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)
    from app.auth import auth_bp
    from app.users import users_bp
    
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    
    from app.skills import skills_bp
    app.register_blueprint(skills_bp, url_prefix="/users")
    
    from app.internships import internships_bp
    app.register_blueprint(internships_bp, url_prefix="/internships")
    
    from app.submissions import submissions_bp
    app.register_blueprint(submissions_bp, url_prefix="/submissions")




    return app
