from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import text

from app.extensions import db


"""
Volunteer <-> User
"""


class Volunteer(db.Model):
    __tablename__ = 'user_volunteer'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True,
                   autoincrement=True, primary_key=True)
    # ---- Relationships ---- #
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user_table.id'), primary_key=True)
    # ---- Other fields ---- #
    organization = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date_range = db.Column(db.String(25))
    cause = db.Column(db.String(50))
    location = db.Column(db.String(80))
    # description = db.Column(db.String(2000))
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def to_dict(self):
        data = {
            'public_id': self.public_id,
            'organization': self.organization,
            'title': self.title,
            'date_range': self.date_range,
            'cause': self.cause,
            'location': self.location,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

        return data

    def from_dict(self, data):
        for field in ['organization', 'title', 'date_range', 'cause', 'location', 'user_id']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<Volunteer {}>'.format(self.id)
