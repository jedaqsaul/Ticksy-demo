from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Event, User, db
from datetime import datetime
from flask import request,make_response, jsonify

# ------------------ Role-Based Decorators ------------------

def organizer_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity())
        if not user or user.role != "organizer":
            return {"message": "Organizer access required"}, 403
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity())
        if not user or user.role != "admin":
            return {"message": "Admin access required"}, 403
        return fn(*args, **kwargs)
    return wrapper

# ------------------ Event Parser ------------------

event_parser = reqparse.RequestParser()
event_parser.add_argument("title", required=True)
event_parser.add_argument("description", required=True)
event_parser.add_argument("location", required=True)
event_parser.add_argument("start_time", required=True)
event_parser.add_argument("end_time", required=True)
event_parser.add_argument("category", required=True)
event_parser.add_argument("tags", required=False)

# ------------------ Organizer: Events CRUD ------------------

class EventList(Resource):
    def get(self):
        # Public endpoint: view approved events
        events = [
            e.to_dict(only=(
                "id", "title", "location", "start_time", "end_time", "category", "tags", "status", "is_approved",
                "organizer.id", "organizer.first_name", "organizer.last_name"
            ))
            for e in Event.query.filter_by(is_approved=True).all()
            ]
        return make_response(jsonify(events), 200)

    @organizer_required
    def post(self):
        data = event_parser.parse_args()
        organizer_id = get_jwt_identity()

        try:
            new_event = Event(
                title=data["title"],
                description=data["description"],
                location=data["location"],
                start_time=datetime.fromisoformat(data["start_time"]),
                end_time=datetime.fromisoformat(data["end_time"]),
                category=data["category"],
                tags=data["tags"],
                organizer_id=organizer_id,
                status="pending",
                is_approved=False
            )
            db.session.add(new_event)
            db.session.commit()
            return new_event.to_dict(), 201
        except Exception as e:
            return {"message": str(e)}, 400


class EventDetail(Resource):
    def get(self, id):
        event = Event.query.get(id)
        if not event:
            return {"message": "Event not found"}, 404
        return event.to_dict(), 200

    @organizer_required
    def put(self, id):
        event = Event.query.get(id)
        if not event:
            return {"message": "Event not found"}, 404
        if event.organizer_id != get_jwt_identity():
            return {"message": "Not authorized to edit this event"}, 403

        data = request.get_json()
        for key in ["title", "description", "location", "category", "tags"]:
            if key in data:
                setattr(event, key, data[key])
        if "start_time" in data:
            event.start_time = datetime.fromisoformat(data["start_time"])
        if "end_time" in data:
            event.end_time = datetime.fromisoformat(data["end_time"])

        db.session.commit()
        return event.to_dict(), 200

    @organizer_required
    def delete(self, id):
        event = Event.query.get(id)
        if not event:
            return {"message": "Event not found"}, 404
        if event.organizer_id != get_jwt_identity():
            return {"message": "Not authorized to delete this event"}, 403

        db.session.delete(event)
        db.session.commit()
        return {"message": "Event deleted successfully"}, 200


class MyEvents(Resource):
    @organizer_required
    def get(self):
        organizer_id = get_jwt_identity()
        events = Event.query.filter_by(organizer_id=organizer_id).all()
        return [e.to_dict() for e in events], 200

# ------------------ Admin: Event Approval ------------------

class PendingEvents(Resource):
    @admin_required
    def get(self):
        events = Event.query.filter_by(is_approved=False).all()
        return [e.to_dict() for e in events], 200


class ApproveEvent(Resource):
    @admin_required
    def patch(self, id):
        event = Event.query.get(id)
        if not event:
            return {"message": "Event not found"}, 404

        data = request.get_json()
        approve = data.get("approve")

        if approve is True:
            event.is_approved = True
            event.status = "active"
            message = "Event approved"
        else:
            event.is_approved = False
            event.status = "rejected"
            message = "Event rejected"

        db.session.commit()
        return {"message": message}
