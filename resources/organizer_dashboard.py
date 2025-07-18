# resources/organizer_dashboard.py

from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Event, Ticket, OrderItem, User
from sqlalchemy import func
from datetime import datetime

# Decorator to ensure user is an organizer
def organizer_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity())
        if not user or user.role != "organizer":
            return {"message": "Organizer access required"}, 403
        return fn(*args, **kwargs)
    return wrapper


class OrganizerOverview(Resource):
    @organizer_required
    def get(self):
        user_id = get_jwt_identity()
        now = datetime.now()

        # Fetch all event IDs for the organizer
        events = Event.query.filter_by(organizer_id=user_id).all()
        event_ids = [e.id for e in events]

        # Correct revenue query (joins Ticket to get price)
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

            stats.append({
                "event_id": e.id,
                "title": e.title,
                "tickets": ticket_stats,
                "total_event_revenue": sum(t["revenue"] for t in ticket_stats)
            })

        return stats, 200
