from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Log, User
from functools import wraps

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity())
        if not user or user.role != "admin":
            return {"message": "Admin access only"}, 403
        return fn(*args, **kwargs)
    return wrapper

class AdminLogs(Resource):
    @admin_required
    def get(self):
        logs = Log.query.order_by(Log.created_at.desc()).limit(50).all()
        return [{
            "id": l.id,
            "user_id": l.user_id,
            "action": l.action,
            "meta_data": l.meta_data,
            "created_at": l.created_at.isoformat()
        } for l in logs], 200
