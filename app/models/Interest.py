from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import text

from app.extensions import db


"""
Independent Model
"""


class Interest(db.Model):
    __tablename__ = 'user_interest'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True, primary_key=True)
    # ---- Basic Interest details ---- #
    name = db.Column(db.String(100), index=True, nullable=False)
    # ---- Meta data ---- #
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def to_dict(self):
        data = {
            'public_id': self.public_id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

        return data

    def __repr__(self):
        return '<Interest {}>'.format(self.id)
