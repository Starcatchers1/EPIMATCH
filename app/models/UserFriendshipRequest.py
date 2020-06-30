from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import text

from app.extensions import db
from .User import User

"""
Association Table

User <-> UserFriendshipRequest
"""


class UserFriendshipRequest(db.Model):
    __tablename__ = 'user_friendship_request'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True,
                   autoincrement=True, primary_key=True)
    # ---- Relationships ---- #
    # ---- User details of whom we are sending a request to ---- #
    to_user_id = db.Column(db.Integer, db.ForeignKey(
        'user_table.id'), primary_key=True)
    to_user = relationship(
        "User", backref="received_requests", primaryjoin=(User.id == to_user_id))
    # ---- User details which is sending the request ---- #
    from_user_id = db.Column(db.Integer, db.ForeignKey(
        'user_table.id'), primary_key=True)
    from_user = relationship(
        "User", backref="sent_requests", primaryjoin=(User.id == from_user_id))
    # ---- Other fields ---- #
    status = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def reject_request(self):
        self.status = 'rejected'

    def from_dict(self, data):
        for field in ['to_user_id', 'to_user', 'from_user_id', 'from_user', 'status']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<UserFriendshipRequest {}>'.format(self.id)
