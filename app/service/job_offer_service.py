from app.extensions import db
from ..models import JobOffer


def save_job_offer(job_offer_data, user):
    job_offer = JobOffer()
    job_offer.from_dict(job_offer_data)
    db.session.add(job_offer)
    user.add_job_offer(job_offer)
    db.session.commit()

    return job_offer.public_id


def get_job_offers(job_offers):
    return list(map(lambda x: x.to_dict(), job_offers))
