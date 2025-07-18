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
            first_name="Celestine", last_name="Mecheo",
            email="celestine@example.com", phone="0700670001",
            password=bcrypt.generate_password_hash("celestine123").decode('utf-8'),
            role="admin"
        )

        organizer1 = User(
            first_name="Oliver", last_name="Organizer",
            email="organizer@example.com", phone="0700000002",
            password=bcrypt.generate_password_hash("organizerpass").decode('utf-8'),
            role="organizer"
        )
        organizer2 = User(
            first_name="Grace", last_name="Kamau",
            email="grace@example.com", phone="0700000004",
            password=bcrypt.generate_password_hash("grace123").decode('utf-8'),
            role="organizer"
        )

        attendee1 = User(
            first_name="Ava", last_name="Attendee",
            email="attendee@example.com", phone="0700000003",
            password=bcrypt.generate_password_hash("attendeepass").decode('utf-8'),
            role="attendee"
        )
        attendee2 = User(
            first_name="John", last_name="Doe",
            email="john@example.com", phone="0700000005",
            password=bcrypt.generate_password_hash("john123").decode('utf-8'),
            role="attendee"
        )

        print("📅 Seeding events...")
        event1 = Event(
            title="Tech Summit Nairobi",
            description="A gathering of top tech leaders.",
            location="KICC",
            start_time=datetime.now() + timedelta(days=5),
            end_time=datetime.now() + timedelta(days=6),
            category="Technology",
            tags="tech,startups,networking",
            status="active",
            is_approved=True,
            organizer=organizer1
        )

        event2 = Event(
            title="Music Fest Kenya",
            description="Enjoy live music from top artists.",
            location="Uhuru Gardens",
            start_time=datetime.now() + timedelta(days=10),
            end_time=datetime.now() + timedelta(days=11),
            category="Entertainment",
            tags="music,festival,fun",
            status="active",
            is_approved=True,
            organizer=organizer2
        )

        print("🎟️ Seeding tickets...")
        ticket1_vip = Ticket(type="VIP", price=5000, quantity=50, event=event1)
        ticket1_regular = Ticket(type="Regular", price=2000, quantity=200, event=event1)

        ticket2_vip = Ticket(type="VIP", price=3000, quantity=30, event=event2)
        ticket2_regular = Ticket(type="Regular", price=1000, quantity=100, event=event2)

        print("🛒 Seeding orders...")
        order1 = Order(
            order_id=str(uuid.uuid4()),
            attendee=attendee1,
            status="paid",
            mpesa_receipt="MPESA123456",
            total_amount=7000
        )
        order_item1 = OrderItem(order=order1, ticket=ticket1_vip, quantity=1)
        order_item2 = OrderItem(order=order1, ticket=ticket1_regular, quantity=1)

        order2 = Order(
            order_id=str(uuid.uuid4()),
            attendee=attendee2,
            status="paid",
            mpesa_receipt="MPESA789456",
            total_amount=4000
        )
        order_item3 = OrderItem(order=order2, ticket=ticket2_vip, quantity=1)
        order_item4 = OrderItem(order=order2, ticket=ticket2_regular, quantity=1)

        print("⭐ Seeding reviews...")
        review1 = Review(
            attendee=attendee1,
            event=event1,
            rating=5,
            comment="Amazing event, well organized!"
        )

        review2 = Review(
            attendee=attendee2,
            event=event2,
            rating=4,
            comment="Great vibe and performances!"
        )

        print("📌 Seeding saved events...")
        saved1 = SavedEvent(user=attendee1, event=event1)
        saved2 = SavedEvent(user=attendee2, event=event2)

        print("✉️ Seeding messages...")
        message1 = Message(
            sender=organizer1,
            recipient=attendee1,
            subject="Welcome to Tech Summit!",
            body="Hi Ava, we look forward to seeing you at the event!"
        )
        message2 = Message(
            sender=organizer2,
            recipient=attendee2,
            subject="Don't miss Music Fest!",
            body="John, it's going to be a blast. Get ready!"
        )

        print("💾 Committing to DB...")
        db.session.add_all([
            admin,
            organizer1, organizer2,
            attendee1, attendee2,
            event1, event2,
            ticket1_vip, ticket1_regular,
            ticket2_vip, ticket2_regular,
            order1, order_item1, order_item2,
            order2, order_item3, order_item4,
            review1, review2,
            saved1, saved2,
            message1, message2
        ])
        db.session.commit()
        print("✅ Seed complete!")

if __name__ == "__main__":
    seed()
