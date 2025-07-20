from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Event, Ticket, OrderItem, User, Review
from sqlalchemy import func
from datetime import datetime
from functools import wraps


# ------------------ Auth Guard ------------------

def organizer_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity())
        if not user or user.role != "organizer":
            return {"message": "Organizer access required"}, 403
        return fn(*args, **kwargs)
    return wrapper


# ------------------ Overview & Stats ------------------

class OrganizerOverview(Resource):
    @organizer_required
    def get(self):
        user_id = get_jwt_identity()
        now = datetime.now()

        events = Event.query.filter_by(organizer_id=user_id).all()
        event_ids = [e.id for e in events]

        total_revenue = db.session.query(func.sum(Ticket.price * OrderItem.quantity))\
            .join(OrderItem.ticket)\
            .join(Ticket.event)\
            .filter(Event.organizer_id == user_id)\
            .scalar() or 0

        total_tickets_sold = db.session.query(func.sum(Ticket.sold))\
            .filter(Ticket.event_id.in_(event_ids)).scalar() or 0

        upcoming = Event.query.filter(Event.organizer_id == user_id, Event.start_time > now).count()
        past = Event.query.filter(Event.organizer_id == user_id, Event.start_time <= now).count()

        return {
            "total_revenue": total_revenue,
            "tickets_sold": total_tickets_sold,
            "upcoming_events": upcoming,
            "past_events": past
        }, 200


class OrganizerEventStats(Resource):
    @organizer_required
    def get(self):
        user_id = get_jwt_identity()
        events = Event.query.filter_by(organizer_id=user_id).all()

        stats = []
        for e in events:
            ticket_stats = []
            for t in e.tickets:
                ticket_stats.append({
                    "type": t.type,
                    "price": t.price,
                    "sold": t.sold,
                    "revenue": t.price * t.sold
                })

            average_rating = db.session.query(func.avg(Review.rating))\
                .filter(Review.event_id == e.id).scalar()

            stats.append({
                "event_id": e.id,
                "title": e.title,
                "tickets": ticket_stats,
                "total_event_revenue": sum(t["revenue"] for t in ticket_stats),
                "average_rating": round(average_rating, 1) if average_rating else None
            })

        return stats, 200


# ------------------ Event Lists by Status ------------------

class OrganizerEventsByStatus(Resource):
    @organizer_required
    def get(self, status):
        user_id = get_jwt_identity()
        valid_statuses = ["approved", "pending", "rejected"]
        if status not in valid_statuses:
            return {"message": "Invalid status"}, 400

        events = Event.query.filter_by(organizer_id=user_id, status=status).all()

        return [
            {
                "id": e.id,
                "title": e.title,
                "image_url": e.image_url,
                "view_link": f"/events/{e.id}"
            }
            for e in events
        ], 200


class OrganizerEventHistory(Resource):
    @organizer_required
    def get(self):
        user_id = get_jwt_identity()
        now = datetime.now()
        events = Event.query.filter(Event.organizer_id == user_id, Event.end_time < now).all()

        return [
            {
                "id": e.id,
                "title": e.title,
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat(),
                "image_url": e.image_url,
                "status": e.status,
                "view_link": f"/events/{e.id}"
            }
            for e in events
        ], 200
