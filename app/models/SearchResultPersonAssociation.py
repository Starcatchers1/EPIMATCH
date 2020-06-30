from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import text

from app.extensions import db

"""
Association Table

SearchResultPerson <-> SearchResultPersonAssociation <-> User
"""


class SearchResultPersonAssociation(db.Model):
    __tablename__ = 'search_result_person_association'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True,
                   autoincrement=True, primary_key=True)
    # ---- Relationships ---- #
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user_table.id'), primary_key=True)
    search_result_person_id = db.Column(db.Integer, db.ForeignKey(
        'search_result_person.id'), primary_key=True)
    search_result = relationship('SearchResultPerson')
    # ---- Other fields ---- #
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def from_dict(self, data):
        for field in ['search_result_person_id', 'user_id', 'search_result']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<SearchResultPersonAssociation {}>'.format(self.id)
