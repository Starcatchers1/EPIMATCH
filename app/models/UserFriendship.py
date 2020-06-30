from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import text

from app.extensions import db


"""
UserMatch <-> UserFriendship <-> UserMatch

This model can store additional symmetrical info (common for both sides)
"""


class UserFriendship(db.Model):
    __tablename__ = 'user_friendship'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True,
                   autoincrement=True, primary_key=True)
    # ---- Relationships ---- #
    parties = relationship(
        "UserMatch", back_populates="friendship", cascade='save-update, merge, delete')
    # ---- Meta data ---- #
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def __repr__(self):
        return '<UserFriendship {}>'.format(self.id)
