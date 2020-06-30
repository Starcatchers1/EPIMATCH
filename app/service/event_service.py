from app.extensions import db
from ..models import Event


def save_event(event_data, user):
    event = Event()
    event.from_dict(event_data)
    db.session.add(event)
    user.add_event(event)
    db.session.commit()

    return event.public_id


def get_events(events):
    return list(map(lambda x: x.to_dict(), events))
