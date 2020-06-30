from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import text


from app.extensions import db


"""
JobOffer <-> User
"""


class JobOffer(db.Model):
    __tablename__ = 'user_job_offer'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True,
                   autoincrement=True, primary_key=True)
    # ---- Relationships ---- #
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user_table.id'), primary_key=True)
    # ---- Basic JobOffer details ---- #
    title = db.Column(db.String(255), nullable=False)
    venue = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(280), nullable=False)
    contact = db.Column(db.String(80), nullable=False)
    starts_at = db.Column(db.DateTime, index=True, nullable=False)
    # ---- Meta data ---- #
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def to_dict(self):
        data = {
            'public_id': self.public_id,
            'title': self.title,
            'venue': self.venue,
            'location': self.title,
            'description': self.description,
            'contact': self.contact,
            'starts_at': self.starts_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

        return data

    def from_dict(self, data):
        for field in ['user_id', 'title', 'venue', 'location', 'description', 'contact', 'starts_at']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<JobOffer {}>'.format(self.id)
