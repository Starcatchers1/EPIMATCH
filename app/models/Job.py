from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import text

from app.extensions import db


"""
Association table

Company <-> Job <-> User
"""

# https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#association-object


class Job(db.Model):
    __tablename__ = 'user_job'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True,
                   autoincrement=True, primary_key=True)
    # ---- Relationships ---- #
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user_table.id'), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey(
        'linkedin_company.id'), primary_key=True)
    company = relationship('Company')
    # ---- Other fields ---- #
    title = db.Column(db.String(100), nullable=False)
    date_range = db.Column(db.String(25), nullable=False)
    location = db.Column(db.String(80))
    current = db.Column(db.Boolean, unique=False, default=False)
    # description = db.Column(db.String(2000))
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def from_dict(self, data):
        for field in ['title', 'date_range', 'location', 'current', 'user_id', 'company_id', 'company']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<Job {}>'.format(self.id)
