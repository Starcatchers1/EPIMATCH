from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import text

from app.extensions import db

"""
Independent Model
"""


class Education(db.Model):
    __tablename__ = 'linkedin_education'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True, primary_key=True)
    # ---- Basic Education details ---- #
    school = db.Column(db.String(150), index=True, nullable=False)
    # ---- Meta data ---- #
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def to_dict(self):
        data = {
            'public_id': self.public_id,
            'school': self.school,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

        return data

    def __repr__(self):
        return '<Education {}>'.format(self.id)
