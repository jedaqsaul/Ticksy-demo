# from flask_restful import Resource, reqparse
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from models import db, Message, User
# from datetime import datetime

# message_parser = reqparse.RequestParser()
# message_parser.add_argument("recipient_id", type=int, required=True)
# message_parser.add_argument("subject", type=str, required=False)
# message_parser.add_argument("body", type=str, required=True)

# class SendMessage(Resource):
#     @jwt_required()
#     def post(self):
#         sender_id = get_jwt_identity()
#         data = message_parser.parse_args()

#         recipient = User.query.get(data["recipient_id"])
#         if not recipient:
#             return {"message": "Recipient not found"}, 404

#         message = Message(
#             sender_id=sender_id,
#             recipient_id=data["recipient_id"],
#             subject=data.get("subject"),
#             body=data["body"],
#             sent_at=datetime.now()
#         )

#         db.session.add(message)
#         db.session.commit()

#         return message.to_dict(only=(
#             "id", "subject", "body", "read_status", "sent_at",
#             "sender.id", "sender.first_name", "sender.last_name",
#             "recipient.id", "recipient.first_name", "recipient.last_name"
#         )), 201

# class UserMessages(Resource):
#     @jwt_required()
#     def get(self):
#         user_id = get_jwt_identity()
#         messages = Message.query.filter_by(recipient_id=user_id).order_by(Message.sent_at.desc()).all()
#         return [
#             m.to_dict(only=(
#                 "id", "subject", "body", "read_status", "sent_at",
#                 "sender.id", "sender.first_name", "sender.last_name"
#             )) for m in messages
#         ], 200
