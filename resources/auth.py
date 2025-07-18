# resources/auth.py
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse
from flask import request
from flask_jwt_extended import create_access_token
from models import User, db
from flask_bcrypt import Bcrypt
from datetime import timedelta

bcrypt = Bcrypt()

# ----------------- Parsers -----------------

signup_parser = reqparse.RequestParser()
signup_parser.add_argument("first_name", required=True)
signup_parser.add_argument("last_name", required=True)
signup_parser.add_argument("email", required=True)
signup_parser.add_argument("phone", required=True)
signup_parser.add_argument("password", required=True)
signup_parser.add_argument("role")

login_parser = reqparse.RequestParser()
login_parser.add_argument("email", required=True)
login_parser.add_argument("password", required=True)

# ----------------- Resources -----------------

class Register(Resource):
    def post(self):
        data = signup_parser.parse_args()

        # Check if user already exists
        if User.query.filter_by(email=data["email"]).first():
            return {"message": "Email already registered."}, 400
        if User.query.filter_by(phone=data["phone"]).first():
            return {"message": "Phone number already registered."}, 400

        # Validate role
        requested_role = data.get("role", "attendee").lower()
        if requested_role not in ["attendee", "organizer"]:
            requested_role = "attendee"

        # Hash password
        hashed_pw = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

        new_user = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data["phone"],
            password=hashed_pw,
            role=requested_role
        )

        db.session.add(new_user)
        db.session.commit()

        token = create_access_token(identity=new_user.id, expires_delta=timedelta(hours=24))

        return {
            "message": "User registered successfully.",
            "user": {
                "id": new_user.id,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "email": new_user.email,
                "role": new_user.role
            },
            "access_token": token
        }, 201



class Login(Resource):
    def post(self):
        data = login_parser.parse_args()

        user = User.query.filter_by(email=data["email"]).first()

        if not user or not bcrypt.check_password_hash(user.password, data["password"]):
            return {"message": "Invalid email or password."}, 401

        token = create_access_token(identity=user.id, expires_delta=timedelta(hours=24))

        return {
            "message": "Login successful.",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.role
            },
            "access_token": token
        }, 200
    
class Me(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return {"message": "User not found"}, 404

        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "status": user.status,
        }, 200
    

