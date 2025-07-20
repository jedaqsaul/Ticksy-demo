from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User

profile_parser = reqparse.RequestParser()
profile_parser.add_argument("first_name", type=str)
profile_parser.add_argument("last_name", type=str)
profile_parser.add_argument("email", type=str)
profile_parser.add_argument("phone", type=str)
profile_parser.add_argument("status", type=str)

def serialize_user(user):
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "status": user.status,
    }

class MyProfile(Resource):
    @jwt_required()
    def get(self):
        user = User.query.get(get_jwt_identity())
        if not user:
            return {"message": "User not found"}, 404
        return serialize_user(user), 200

    @jwt_required()
    def put(self):
        user = User.query.get(get_jwt_identity())
        data = profile_parser.parse_args()

        for field in data:
            if data[field] is not None:
                setattr(user, field, data[field])

        db.session.commit()
        return serialize_user(user), 200

class ViewUserProfile(Resource):
    @jwt_required()
    def get(self, id):
        user = User.query.get(id)
        if not user:
            return {"message": "User not found"}, 404
        return serialize_user(user), 200
