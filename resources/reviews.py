from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from models import db, Event, Review, User

review_parser = reqparse.RequestParser()
review_parser.add_argument("rating", type=int, required=True)
review_parser.add_argument("comment", type=str, required=False)


class AddReview(Resource):
    @jwt_required()
    def post(self, event_id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user.role != "attendee":
            return {"message": "Only attendees can review"}, 403

        existing = Review.query.filter_by(attendee_id=user_id, event_id=event_id).first()
        if existing:
            return {"message": "You already reviewed this event"}, 400

        data = review_parser.parse_args()
        if not (1 <= data["rating"] <= 5):
            return {"message": "Rating must be between 1 and 5"}, 400

        new_review = Review(
            attendee_id=user_id,
            event_id=event_id,
            rating=data["rating"],
            comment=data["comment"]
        )

        db.session.add(new_review)
        db.session.commit()

        return new_review.to_dict(only=(
            "id", "rating", "comment", "created_at",
            "attendee.id", "attendee.first_name", "attendee.last_name"
        )), 201


class EventReviews(Resource):
    def get(self, event_id):
        reviews = Review.query.options(joinedload(Review.attendee)).filter_by(event_id=event_id).all()
        return [
            r.to_dict(only=(
                "id", "rating", "comment", "created_at",
                "attendee.id", "attendee.first_name", "attendee.last_name"
            ))
            for r in reviews
        ], 200
