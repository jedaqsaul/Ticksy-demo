# resources/users.py

from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, db
from functools import wraps
from flask import request


# ----------------- Role-based Decorator -----------------
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity())
        if not user or user.role != "admin":
            return {"message": "Admin access required"}, 403
        return fn(*args, **kwargs)
    return wrapper


# ----------------- Resources -----------------

class Users(Resource):
    @admin_required
    def get(self):
        users = User.query.all()
        return [
            {
                "id": u.id,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "email": u.email,
                "role": u.role,
                "status": u.status
            }
            for u in users
        ]


class UserById(Resource):
    @admin_required
    def get(self, id):
        user = User.query.get(id)
        if not user:
            return {"message": "User not found"}, 404

        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "status": user.status
        }

    @admin_required
    def delete(self, id):
        user = User.query.get(id)
        if not user:
            return {"message": "User not found"}, 404

        db.session.delete(user)
        db.session.commit()
        return {"message": f"User {id} deleted successfully"}, 200


class UserStatus(Resource):
    @admin_required
    def patch(self, id):
        user = User.query.get(id)
        if not user:
            return {"message": "User not found"}, 404

        data = request.get_json()
        new_status = data.get("status")

        if new_status not in ["active", "banned", "pending"]:
            return {"message": "Invalid status"}, 400

        user.status = new_status
        db.session.commit()
        return {"message": f"User status updated to {new_status}"}


class UserRole(Resource):
    @admin_required
    def patch(self, id):
        user = User.query.get(id)
        if not user:
            return {"message": "User not found"}, 404

        data = request.get_json()
        new_role = data.get("role")

        if new_role not in ["attendee", "organizer", "admin"]:
            return {"message": "Invalid role"}, 400

        user.role = new_role
        db.session.commit()
        return {"message": f"User role updated to {new_role}"}
