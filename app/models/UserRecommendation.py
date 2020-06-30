from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import text

from app.extensions import db
from .User import User

"""
Association Table

User <-> UserRecommendation <-> User
"""


class UserRecommendation(db.Model):
    __tablename__ = 'user_recommendation'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True,
                   autoincrement=True, primary_key=True)
    # ---- Relationships ---- #
    # ---- User details of whom we are recommending a user to ---- #
    recommended_for_id = db.Column(db.Integer, db.ForeignKey(
        'user_table.id'), primary_key=True)
    recommended_for = relationship(
        "User", backref="recommended_list", primaryjoin=(User.id == recommended_for_id))
    # ---- User details which is in the recommended list ---- #
    recommended_id = db.Column(db.Integer, db.ForeignKey(
        'user_table.id'), primary_key=True)
    recommended = relationship(
        "User", backref="recommended_for_list", primaryjoin=(User.id == recommended_id))
    # ---- Other fields ---- #
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def from_dict(self, data):
        for field in ['recommended_for_id', 'recommended_for', 'recommended_id', 'recommended']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<UserRecommendation {}>'.format(self.id)
