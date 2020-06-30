from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import text

from app.extensions import db

"""
Independent Model
"""


class Company(db.Model):
    __tablename__ = 'linkedin_company'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True, primary_key=True)
    # ---- Basic Company details ---- #
    name = db.Column(db.String(100), index=True, nullable=False)
    url = db.Column(db.String(256))
    # ---- Meta data ---- #
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def to_dict(self):
        data = {
            'public_id': self.public_id,
            'name': self.name,
            'url': self.url,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

        return data

    def from_dict(self, data):
        for field in ['name', 'url']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<Company {}>'.format(self.id)
