# app.py

import os
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta

from models import db
from resources.auth import Register, Login, Me  # ✅ import auth routes

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///development.db"  # dev only
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "your_jwt_secret"  # temp secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

# Extensions
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
CORS(app)
api = Api(app)

# Health Check
@app.route("/")
def home():
    return {"message": "Event Ticketing Backend running"}

# JWT error handler
@jwt.unauthorized_loader
def missing_token(error):
    return {
        "message": "Authorization required",
        "success": False,
        "errors": ["Authorization token is required"],
    }, 401

# Register API Resources
api.add_resource(Register, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Me, "/me") 

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
