# resources/tickets.py

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Ticket, Event, User, db
from flask import request

# ------------------ Organizer Decorator ------------------

def organizer_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity())
        if not user or user.role != "organizer":
            return {"message": "Organizer access required"}, 403
        return fn(*args, **kwargs)
    return wrapper

# ------------------ Parser ------------------

ticket_parser = reqparse.RequestParser()
ticket_parser.add_argument("type", required=True)
ticket_parser.add_argument("price", type=float, required=True)
ticket_parser.add_argument("quantity", type=int, required=True)

# ------------------ Resources ------------------

class TicketList(Resource):
    def get(self, event_id):
        tickets = Ticket.query.filter_by(event_id=event_id).all()
        return [t.to_dict() for t in tickets], 200

    @organizer_required
    def post(self, event_id):
        data = ticket_parser.parse_args()
        organizer_id = get_jwt_identity()

        event = Event.query.get(event_id)
        if not event:
            return {"message": "Event not found"}, 404
        if event.organizer_id != organizer_id:
            return {"message": "You are not authorized to add tickets to this event"}, 403

        new_ticket = Ticket(
            type=data["type"],
            price=data["price"],
            quantity=data["quantity"],
            event_id=event_id
        )

        db.session.add(new_ticket)
        db.session.commit()
        return new_ticket.to_dict(), 201


class TicketDetail(Resource):
    @organizer_required
    def put(self, id):
        ticket = Ticket.query.get(id)
        if not ticket:
            return {"message": "Ticket not found"}, 404

        user_id = get_jwt_identity()
        if ticket.event.organizer_id != user_id:
            return {"message": "Unauthorized"}, 403

        data = request.get_json()
        for key in ["type", "price", "quantity"]:
            if key in data:
                setattr(ticket, key, data[key])

        db.session.commit()
        return ticket.to_dict(), 200

    @organizer_required
    def delete(self, id):
        ticket = Ticket.query.get(id)
        if not ticket:
            return {"message": "Ticket not found"}, 404

        user_id = get_jwt_identity()
        if ticket.event.organizer_id != user_id:
            return {"message": "Unauthorized"}, 403

        db.session.delete(ticket)
        db.session.commit()
        return {"message": "Ticket deleted successfully"}, 200