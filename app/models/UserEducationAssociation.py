from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import text

from app.extensions import db

"""
Association Table

Education <-> UserEducationAssociation <-> User
"""


class UserEducationAssociation(db.Model):
    __tablename__ = 'user_education_association'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True,
                   autoincrement=True, primary_key=True)
    # ---- Relationships ---- #
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user_table.id'), primary_key=True)
    education_id = db.Column(db.Integer, db.ForeignKey(
        'linkedin_education.id'), primary_key=True)
    education = relationship('Education')
    # ---- Other fields ---- #
    degree = db.Column(db.String(100))
    field_of_study = db.Column(db.String(100))
    date_range = db.Column(db.String(20))
    grades = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def from_dict(self, data):
        for field in ['education_id', 'user_id', 'degree', 'field_of_study', 'date_range', 'grades', 'education']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<UserEducationAssociation {}>'.format(self.id)
