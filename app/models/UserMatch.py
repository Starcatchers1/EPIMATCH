from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import text


from .UserFriendship import UserFriendship
from app.extensions import db

"""
User -> UserMatch <-> UserFriendship <-> UserMatch -> User

This model can store additional info assymmetrical (different for each side)
like a welcome message
"""


class UserMatch(db.Model):
    __tablename__ = 'user_match'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True,
                   autoincrement=True, primary_key=True)
    # ---- Relationships ---- #
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user_table.id'), primary_key=True)
    friendship_id = db.Column(db.Integer, db.ForeignKey(
        'user_friendship.id'), primary_key=True)
    friendship = relationship(
        "UserFriendship", back_populates="parties", cascade='save-update, merge, delete')
    # ---- Meta data ---- #
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def other_party(self):
        return (self.friendship.parties[0] if self.friendship.parties[0] != self else self.friendship.parties[1])

    def __repr__(self):
        return '<UserMatch {}>'.format(self.id)
