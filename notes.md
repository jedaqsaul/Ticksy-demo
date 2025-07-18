## Authentication routes

| Method | Endpoint  | Description             |
| ------ | --------- | ----------------------- |
| POST   | `/signup` | User registration       |
| POST   | `/login`  | User login (JWT issued) |

## User profile routes

| Method | Endpoint      | Description                     |
| ------ | ------------- | ------------------------------- |
| GET    | `/profile/me` | Get logged-in user's profile    |
| PUT    | `/profile/me` | Update logged-in user's profile |
| GET    | `/users/<id>` | Admin view of any user profile  |

## Event routes(public and organizer)

| Method | Endpoint       | Description                                 |
| ------ | -------------- | ------------------------------------------- |
| GET    | `/events`      | Public: list of approved events             |
| POST   | `/events`      | Organizer: create new event                 |
| GET    | `/events/<id>` | Public: view event details (+calendar link) |
| PUT    | `/events/<id>` | Organizer: update own event                 |
| DELETE | `/events/<id>` | Organizer: delete own event                 |
| GET    | `/my-events`   | Organizer: list own events                  |

## Admin event moderation

| Method | Endpoint              | Description                |
| ------ | --------------------- | -------------------------- |
| GET    | `/admin/pending`      | List unapproved events     |
| PATCH  | `/admin/approve/<id>` | Approve or reject an event |

## Admin reports

| Method | Endpoint         | Description                          |
| ------ | ---------------- | ------------------------------------ |
| GET    | `/admin/reports` | Filtered report by date & event name |

## Organizer dashboard and analytics

| Method | Endpoint              | Description                               |
| ------ | --------------------- | ----------------------------------------- |
| GET    | `/organizer/overview` | Total revenue, tickets sold, event counts |
| GET    | `/organizer/stats`    | Detailed stats per event & ticket types   |

### what is missing?

- calender intergration
- messaging
