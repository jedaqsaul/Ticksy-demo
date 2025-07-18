# models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
import re

# Metadata naming convention
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)

# ------------------ User ------------------
class User(db.Model, SerializerMixin):
    __tablename__ = "users"
    serialize_rules = ("-password", "-messages_sent.sender", "-messages_received.recipient")

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="attendee")  # attendee, organizer, admin
    status = db.Column(db.String(20), default="active")
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    events = db.relationship("Event", back_populates="organizer", cascade="all, delete")
    orders = db.relationship("Order", back_populates="attendee", cascade="all, delete")
    reviews = db.relationship("Review", back_populates="attendee", cascade="all, delete")
    saved_events = db.relationship("SavedEvent", back_populates="user", cascade="all, delete")
    messages_sent = db.relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    messages_received = db.relationship("Message", back_populates="recipient", foreign_keys="Message.recipient_id")
    logs = db.relationship("Log", back_populates="user")
    reports = db.relationship("Report", back_populates="admin")

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"

    @validates("email")
    def validate_email(self, key, value):
        normalized = value.strip().lower()
        reg = r"[A-Za-z][A-Za-z0-9]*(\.[A-Za-z0-9]+)*@[A-Za-z0-9]+\.[a-z]{2,}"
        if not re.match(reg, normalized):
            raise ValueError("Invalid email format")
        return normalized


# ------------------ Event ------------------
class Event(db.Model, SerializerMixin):
    __tablename__ = "events"
    serialize_rules = ("-organizer.events", "-tickets.event", "-reviews.event", "-saved_events.event")

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String)
    tags = db.Column(db.String)
    is_approved = db.Column(db.Boolean, default=False)
    status = db.Column(db.String, default="pending")  # active, pending, cancelled
    created_at = db.Column(db.DateTime, default=datetime.now)

    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    organizer = db.relationship("User", back_populates="events")
    tickets = db.relationship("Ticket", back_populates="event", cascade="all, delete")
    reviews = db.relationship("Review", back_populates="event", cascade="all, delete")
    saved_events = db.relationship("SavedEvent", back_populates="event", cascade="all, delete")
    reports = db.relationship("Report", back_populates="event")


# ------------------ Ticket ------------------
class Ticket(db.Model, SerializerMixin):
    __tablename__ = "tickets"
    serialize_rules = ("-event.tickets", "-order_items.ticket")

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)  # VIP, Early Bird, Regular
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sold = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))
    event = db.relationship("Event", back_populates="tickets")
    order_items = db.relationship("OrderItem", back_populates="ticket")


# ------------------ Order ------------------
class Order(db.Model, SerializerMixin):
    __tablename__ = "orders"
    serialize_rules = ("-attendee.orders", "-order_items.order")

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String, nullable=False, unique=True)
    status = db.Column(db.String, default="pending")  # pending, paid, failed
    mpesa_receipt = db.Column(db.String)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    attendee_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    attendee = db.relationship("User", back_populates="orders")
    order_items = db.relationship("OrderItem", back_populates="order", cascade="all, delete")


# ------------------ OrderItem ------------------
class OrderItem(db.Model, SerializerMixin):
    __tablename__ = "order_items"
    serialize_rules = ("-order.order_items", "-ticket.order_items")

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"))

    order = db.relationship("Order", back_populates="order_items")
    ticket = db.relationship("Ticket", back_populates="order_items")


# ------------------ Review ------------------
class Review(db.Model, SerializerMixin):
    __tablename__ = "reviews"
    serialize_rules = ("-attendee.reviews", "-event.reviews")

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    attendee_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    attendee = db.relationship("User", back_populates="reviews")
    event = db.relationship("Event", back_populates="reviews")


# ------------------ SavedEvent ------------------
class SavedEvent(db.Model, SerializerMixin):
    __tablename__ = "saved_events"
    serialize_rules = ("-user.saved_events", "-event.saved_events")

    id = db.Column(db.Integer, primary_key=True)
    saved_at = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    user = db.relationship("User", back_populates="saved_events")
    event = db.relationship("Event", back_populates="saved_events")


# ------------------ Message ------------------
class Message(db.Model, SerializerMixin):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String)
    body = db.Column(db.Text)
    read_status = db.Column(db.String, default="unread")
    sent_at = db.Column(db.DateTime, default=datetime.now)

    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    sender = db.relationship("User", back_populates="messages_sent", foreign_keys=[sender_id])
    recipient = db.relationship("User", back_populates="messages_received", foreign_keys=[recipient_id])


# ------------------ Report ------------------
class Report(db.Model, SerializerMixin):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    generated_at = db.Column(db.DateTime, default=datetime.now)
    report_data = db.Column(db.Text)

    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    admin = db.relationship("User", back_populates="reports")
    event = db.relationship("Event", back_populates="reports")


# ------------------ Log ------------------
class Log(db.Model, SerializerMixin):
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String)
    meta_data = db.Column(db.Text)  # <- renamed from 'metadata'
    created_at = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User", back_populates="logs")

