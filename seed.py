# seed.py

from app import app, db
from models import User, Event, Ticket, Order, OrderItem, Review, SavedEvent, Message
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import uuid

bcrypt = Bcrypt()

def seed():
    with app.app_context():
        print("🔁 Dropping and creating all tables...")
        db.drop_all()
        db.create_all()

        print("👤 Seeding users...")
        admin = User(
            first_name="Alice", last_name="Admin",
            email="admin@example.com", phone="0700000001",
            password=bcrypt.generate_password_hash("adminpass").decode('utf-8'),
            role="admin"
        )
        organizer = User(
            first_name="Oliver", last_name="Organizer",
            email="organizer@example.com", phone="0700000002",
            password=bcrypt.generate_password_hash("organizerpass").decode('utf-8'),
            role="organizer"
        )
        attendee = User(
            first_name="Ava", last_name="Attendee",
            email="attendee@example.com", phone="0700000003",
            password=bcrypt.generate_password_hash("attendeepass").decode('utf-8'),
            role="attendee"
        )

        print("📅 Seeding event...")
        event = Event(
            title="Tech Summit Nairobi",
            description="A gathering of top tech leaders.",
            location="KICC",
            start_time=datetime.now() + timedelta(days=5),
            end_time=datetime.now() + timedelta(days=6),
            category="Technology",
            tags="tech,startups,networking",
            status="active",
            is_approved=True,
            organizer=organizer
        )

        print("🎟️ Seeding tickets...")
        vip = Ticket(type="VIP", price=5000, quantity=50, event=event)
        regular = Ticket(type="Regular", price=2000, quantity=200, event=event)

        print("🛒 Seeding order...")
        order = Order(
            order_id=str(uuid.uuid4()),
            attendee=attendee,
            status="paid",
            mpesa_receipt="MPESA123456",
            total_amount=7000
        )
        order_item1 = OrderItem(order=order, ticket=vip, quantity=1)
        order_item2 = OrderItem(order=order, ticket=regular, quantity=1)

        print("⭐ Seeding review...")
        review = Review(
            attendee=attendee,
            event=event,
            rating=5,
            comment="Amazing event, well organized!"
        )

        print("📌 Seeding saved event...")
        saved_event = SavedEvent(user=attendee, event=event)

        print("✉️ Seeding message...")
        message = Message(
            sender=organizer,
            recipient=attendee,
            subject="Welcome to Tech Summit!",
            body="Hi Ava, we look forward to seeing you at the event!",
        )

        print("💾 Committing to DB...")
        db.session.add_all([
            admin, organizer, attendee,
            event, vip, regular,
            order, order_item1, order_item2,
            review, saved_event, message
        ])
        db.session.commit()
        print("✅ Seed complete!")

if __name__ == "__main__":
    seed()
