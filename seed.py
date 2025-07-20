from models import db, User, Event, Ticket, Order, OrderItem, Review, Report, Log
from app import app, bcrypt  # 👈 Make sure bcrypt is imported from app
from datetime import datetime, timedelta
import random

with app.app_context():
    print("🧹 Cleaning database...")
    Log.query.delete()
    Report.query.delete()
    Review.query.delete()
    OrderItem.query.delete()
    Order.query.delete()
    Ticket.query.delete()
    Event.query.delete()
    User.query.delete()

    db.session.commit()

    print("🌱 Seeding users...")
    users = []

    # Admins
    users.append(User(first_name="Alice", last_name="Admin", email="alice@admin.com", phone="0700000001", password=bcrypt.generate_password_hash("admin123").decode('utf-8'), role="admin"))
    users.append(User(first_name="Bob", last_name="Boss", email="bob@admin.com", phone="0700000002", password=bcrypt.generate_password_hash("admin123").decode('utf-8'), role="admin"))
    users.append(User(first_name="Celestine", last_name="Mecheo", email="celestine@example.com", phone="0700000062", password=bcrypt.generate_password_hash("celestine123").decode('utf-8'), role="admin"))

    # Organizers
    for i in range(1, 4):
        users.append(User(
            first_name=f"Organizer{i}",
            last_name="Org",
            email=f"org{i}@events.com",
            phone=f"070100000{i}",
            password=bcrypt.generate_password_hash("org123").decode('utf-8'),
            role="organizer"
        ))

    # Attendees
    for i in range(1, 6):
        users.append(User(
            first_name=f"Attendee{i}",
            last_name="User",
            email=f"attendee{i}@mail.com",
            phone=f"071000000{i}",
            password=bcrypt.generate_password_hash("pass123").decode('utf-8'),
            role="attendee"
        ))

    db.session.add_all(users)
    db.session.commit()

    print("🌱 Seeding events & tickets...")
    events = []
    tickets = []

    for i in range(1, 6):
        organizer = users[2 + (i % 3)]
        event = Event(
            title=f"Event {i}",
            description=f"This is the description for Event {i}.",
            location="Nairobi",
            start_time=datetime.now() + timedelta(days=i),
            end_time=datetime.now() + timedelta(days=i, hours=3),
            category="Music",
            tags="live,concert",
            status=random.choice(["approved", "pending", "rejected"]),
            is_approved=True if i % 2 == 0 else False,
            image_url=f"https://example.com/event{i}.jpg",
            organizer_id=organizer.id,
            attendee_count=0
        )
        db.session.add(event)
        db.session.flush()
        events.append(event)

        for j in range(1, 3):
            t = Ticket(
                type=f"General {j}",
                price=500 + j * 100,
                quantity=100,
                sold=random.randint(10, 50),
                event_id=event.id
            )
            db.session.add(t)
            tickets.append(t)

    db.session.commit()

    print("🌱 Seeding orders, items, reviews...")
    for attendee in users[-5:]:
        for i in range(2):
            ticket = random.choice(tickets)
            quantity = random.randint(1, 3)
            order = Order(
                order_id=f"ORD-{attendee.id}-{i}",
                attendee_id=attendee.id,
                status="paid",
                total_amount=ticket.price * quantity,
                mpesa_receipt=f"MPESA{random.randint(100000,999999)}"
            )
            db.session.add(order)
            db.session.flush()

            item = OrderItem(order_id=order.id, ticket_id=ticket.id, quantity=quantity)
            db.session.add(item)

            ticket.event.attendee_count += quantity
            db.session.flush()

            if random.choice([True, False]):
                review = Review(
                    rating=random.randint(3, 5),
                    comment="Great event!" if i % 2 == 0 else "Could be better.",
                    attendee_id=attendee.id,
                    event_id=ticket.event.id
                )
                db.session.add(review)

    db.session.commit()

    print("🌱 Seeding reports & logs...")
    for admin in users[:2]:
        r = Report(
            report_data="Sample analytics report for system performance.",
            admin_id=admin.id,
            event_id=random.choice(events).id
        )
        db.session.add(r)

        log = Log(
            action="Banned user" if random.choice([True, False]) else "Approved event",
            meta_data="Automated seed action",
            user_id=admin.id
        )
        db.session.add(log)

    db.session.commit()
    print("✅ Seeding complete!")
