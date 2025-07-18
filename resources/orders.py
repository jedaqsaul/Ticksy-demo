# resources/orders.py

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import Order, OrderItem, Ticket, User, db
import uuid
from datetime import datetime

order_parser = reqparse.RequestParser()
order_parser.add_argument("ticket_id", type=int, required=True)
order_parser.add_argument("quantity", type=int, required=True)


class OrderList(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        orders = Order.query.filter_by(attendee_id=user_id).all()
        return [o.to_dict() for o in orders], 200

    @jwt_required()
    def post(self):
        data = order_parser.parse_args()
        user_id = get_jwt_identity()

        ticket = Ticket.query.get(data["ticket_id"])
        if not ticket:
            return {"message": "Ticket not found"}, 404

        if data["quantity"] > (ticket.quantity - ticket.sold):
            return {"message": "Not enough tickets available"}, 400

        total = ticket.price * data["quantity"]

        order = Order(
            order_id=str(uuid.uuid4()),
            attendee_id=user_id,
            status="pending",
            total_amount=total,
            created_at=datetime.now()
        )

        item = OrderItem(
            ticket_id=ticket.id,
            quantity=data["quantity"],
            order=order
        )

        # Update sold count
        ticket.sold += data["quantity"]

        db.session.add(order)
        db.session.add(item)
        db.session.commit()

        return {
            "message": "Order placed. Proceed to payment.",
            "order": order.to_dict()
        }, 201


class OrderDetail(Resource):
    @jwt_required()
    def get(self, id):
        user_id = get_jwt_identity()
        order = Order.query.get(id)

        if not order or order.attendee_id != user_id:
            return {"message": "Order not found or unauthorized"}, 404

        return order.to_dict(), 200
