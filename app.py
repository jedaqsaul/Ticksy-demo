# app.py

import os
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta

from models import db
from resources.auth import Register, Login, Me  
from resources.users import Users, UserById, UserStatus, UserRole
from resources.events import EventList, EventDetail, MyEvents, PendingEvents, ApproveEvent
from resources.tickets import TicketList, TicketDetail
from resources.orders import OrderList, OrderDetail
from resources.payments import STKPush, STKCallback
from resources.reviews import AddReview, EventReviews
from resources.admin import AdminDashboard, AdminReports, AllUsers
# from resources.messages import SendMessage, UserMessages




# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///development.db"  # dev only
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "your_jwt_secret"  # temp secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

# Extensions
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
CORS(app)
api = Api(app)

# Health Check
@app.route("/")
def home():
    return {"message": "Event Ticketing Backend running"}

# JWT error handler
@jwt.unauthorized_loader
def missing_token(error):
    return {
        "message": "Authorization required",
        "success": False,
        "errors": ["Authorization token is required"],
    }, 401

# Register API Resources
api.add_resource(Register, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Me, "/me") 


# user routes

api.add_resource(Users, "/users")
api.add_resource(UserById, "/users/<int:id>")
api.add_resource(UserStatus, "/users/<int:id>/status")
api.add_resource(UserRole, "/users/<int:id>/role")


# event routes

api.add_resource(EventList, "/events")
api.add_resource(EventDetail, "/events/<int:id>")
api.add_resource(MyEvents, "/organizer/events")
api.add_resource(PendingEvents, "/admin/events/pending")
api.add_resource(ApproveEvent, "/admin/events/<int:id>/approve")
api.add_resource(TicketList, "/events/<int:event_id>/tickets")
api.add_resource(TicketDetail, "/tickets/<int:id>")


api.add_resource(OrderList, "/orders")
api.add_resource(OrderDetail, "/orders/<int:id>")
api.add_resource(STKPush, "/payments/stk-push")
api.add_resource(STKCallback, "/payments/callback")


api.add_resource(AddReview, "/events/<int:event_id>/review")
api.add_resource(EventReviews, "/events/<int:event_id>/reviews")


api.add_resource(AdminDashboard, "/admin/dashboard")
api.add_resource(AdminReports, "/admin/reports")
api.add_resource(AllUsers, "/admin/users")

# api.add_resource(SendMessage, "/messages/send")
# api.add_resource(UserMessages, "/messages/inbox")


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
