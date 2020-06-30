from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import text

from app.extensions import db

"""
Association Table

Interest <-> UserInterestAssociation <-> User
"""


class UserInterestAssociation(db.Model):
    __tablename__ = 'user_interest_association'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True,
                   autoincrement=True, primary_key=True)
    # ---- Relationships ---- #
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user_table.id'), primary_key=True)
    interest_id = db.Column(db.Integer, db.ForeignKey(
        'user_interest.id'), primary_key=True)
    interest = relationship('Interest')
    # ---- Other fields ---- #
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def from_dict(self, data):
        for field in ['interest_id', 'user_id', 'interest']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<UserInterestAssociation {}>'.format(self.id)
