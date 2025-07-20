# resources/admin.py

from models import db, User, Event, Ticket, Order, OrderItem
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from datetime import datetime
from sqlalchemy import func
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

class AdminDashboard(Resource):
    @admin_required
    def get(self):
        total_users = User.query.count()
        total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0
        ticket_sales = db.session.query(func.sum(Ticket.sold)).scalar() or 0
        active_events = Event.query.filter_by(status="approved").count()
        pending_events = Event.query.filter_by(status="pending").count()

        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()

        return {
            "totals": {
                "users": total_users,
                "revenue": total_revenue,
                "ticket_sales": ticket_sales,
                "active_events": active_events,
                "pending_events": pending_events,
            },
            "recent_users": [
                {"name": f"{u.first_name} {u.last_name}", "email": u.email}
                for u in recent_users
            ],
            "recent_events": [
                {"title": e.title, "date": e.start_time.isoformat()}
                for e in recent_events
            ]
        }, 200

class AdminReports(Resource):
    @admin_required
    def get(self):
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        event_name = request.args.get("event_name")

        query = db.session.query(Order).join(Order.order_items).join(OrderItem.ticket).join(Ticket.event).join(Order.attendee)

        if start_date:
            start = datetime.fromisoformat(start_date)
            query = query.filter(Order.created_at >= start)

        if end_date:
            end = datetime.fromisoformat(end_date)
            query = query.filter(Order.created_at <= end)

        if event_name:
            query = query.filter(Event.title.ilike(f"%{event_name}%"))

        results = query.all()

        return [
            {
                "order_id": o.order_id,
                "amount": o.total_amount,
                "status": o.status,
                "event": o.order_items[0].ticket.event.title if o.order_items else None,
                "attendee": f"{o.attendee.first_name} {o.attendee.last_name}" if o.attendee else None,
                "date": o.created_at.isoformat()
            }
            for o in results
        ], 200

class AllUsers(Resource):
    @admin_required
    def get(self):
        users = User.query.all()
        return [
            {
                "id": u.id,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "role": u.role,
                "status": u.status,
                "email": u.email
            } for u in users
        ]