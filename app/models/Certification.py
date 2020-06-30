from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import text

from app.extensions import db


"""
Certification <-> User
"""


class Certification(db.Model):
    __tablename__ = 'user_certification'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True,
                   autoincrement=True, primary_key=True)
    # ---- Relationships ---- #
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user_table.id'), primary_key=True)
    # ---- Basic Certification details ---- #
    title = db.Column(db.String(255), nullable=False)
    authority = db.Column(db.String(255), nullable=False)
    date_range = db.Column(db.String(50), nullable=False)
    # ---- Meta data ---- #
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def to_dict(self):
        data = {
            'public_id': self.public_id,
            'title': self.title,
            'authority': self.authority,
            'date_range': self.date_range,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

        return data

    def from_dict(self, data):
        for field in ['title', 'authority', 'date_range', 'user_id']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<Certification {}>'.format(self.id)
