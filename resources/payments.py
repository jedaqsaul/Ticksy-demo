# resources/payments.py

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Order, db
from flask import request

payment_parser = reqparse.RequestParser()
payment_parser.add_argument("order_id", required=True)

class STKPush(Resource):
    @jwt_required()
    def post(self):
        data = payment_parser.parse_args()
        order = Order.query.filter_by(order_id=data["order_id"]).first()

        if not order:
            return {"message": "Order not found"}, 404

        order.status = "paid"
        order.mpesa_receipt = "MPESA-" + str(order.id)
        db.session.commit()

        return {"message": "Payment successful (mocked)", "receipt": order.mpesa_receipt}, 200


class STKCallback(Resource):
    def post(self):
        # Simulate MPESA callback (Daraja logic can go here later)
        return {"message": "Callback received"}, 200
