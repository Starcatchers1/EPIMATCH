from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import text

from app.extensions import db

"""
Independent Model
"""


class SearchResultPerson(db.Model):
    __tablename__ = 'search_result_person'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True, primary_key=True)
    # ---- Basic SearchResultPerson details ---- #
    url = db.Column(db.String(105), index=True, nullable=False)
    scraped = db.Column(db.Boolean, unique=False, default=False)
    # ---- Meta data ---- #
    created_at = db.Column(db.DateTime, index=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def set_scraped(self, status=True):
        self.scraped = status

    def to_dict(self):
        data = {
            'public_id': self.public_id,
            'url': self.url,
            'status': self.scraped,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

        return data

    def from_dict(self, data):
        for field in ['url', 'scraped']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<SearchResultPerson {}>'.format(self.id)
