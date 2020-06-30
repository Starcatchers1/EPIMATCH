from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import text

from .SearchResultPerson import SearchResultPerson
from app.extensions import db

"""
Independent Model
"""


class User(db.Model):
    __tablename__ = 'user_table'

    public_id = db.Column(UUID(as_uuid=True),
                          unique=True,
                          server_default=text("uuid_generate_v4()"))
    id = db.Column(db.Integer, index=True, primary_key=True)
    # ---- Basic User details ---- #
    # See limits at https://theprofile.company/linkedin-profile-character-limit-guide/
    name = db.Column(db.String(60), index=True, nullable=False)
    url = db.Column(db.String(256), index=True, nullable=False)
    image = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(80))
    phone = db.Column(db.String(25))
    location = db.Column(db.String(120))
    connections = db.Column(db.Integer, unique=False, default=0)
    school = db.Column(db.String(120))
    headline = db.Column(db.String(164), nullable=False)
    # Flag to distinguish signed up users from others
    signedup = db.Column(db.Boolean, unique=False, default=False)
    # for users who are signing up
    password_hash = db.Column(db.String(128))
    # ---- Relationships ---- #
    # One To Many #
    certifications = relationship('Certification')
    courses = relationship('Course')
    honors = relationship('Honor')
    languages = relationship('Language')
    organizations = relationship('Organization')
    patents = relationship('Patent')
    projects = relationship('Project')
    publications = relationship('Publication')
    text_scores = relationship('TextScore')
    volunteering = relationship('Volunteer')
    websites = relationship('Website')
    # Other fields
    posts = relationship('Post', backref='author', lazy='dynamic')
    events = relationship('Event', backref='user', lazy='dynamic')
    job_offers = relationship('JobOffer', backref='user', lazy='dynamic')
    # With the cascade configuration, removing a User or UserFriendship or UserMatch make sure both sides are removed.
    friends = relationship('UserMatch', backref='user',
                           cascade='save-update, merge, delete')
    # Associations #
    """
     The left side of the relationship references the association object via one-to-many, and the association class references the right side via many-to-one.
    """
    jobs = relationship('Job', lazy='dynamic',
                        cascade='save-update, merge, delete')
    search_results = relationship(
        'SearchResultPersonAssociation', lazy='dynamic', cascade='save-update, merge, delete')
    education_history = relationship(
        'UserEducationAssociation', lazy='dynamic', cascade='save-update, merge, delete')
    interests = relationship('UserInterestAssociation',
                             lazy='dynamic', cascade='save-update, merge, delete')
    skills = relationship('UserSkillAssociation',
                          lazy='dynamic', cascade='save-update, merge, delete')
    # ---- Meta data ---- #
    created_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())
    updated_at = db.Column(db.DateTime, index=True,
                           server_default=func.now())  # ToDo: fix auto updation

    def set_signedup(self, status=True):
        self.signedup = status

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def change_profile_image(self, image_url):
        self.image = image_url

    def add_certification(self, certification):
        self.certifications.append(certification)

    def add_course(self, course):
        self.courses.append(course)

    def add_honor(self, honor):
        self.honors.append(honor)

    def add_language(self, language):
        self.languages.append(language)

    def add_organization(self, organization):
        self.organizations.append(organization)

    def add_patent(self, patent):
        self.patents.append(patent)

    def add_project(self, project):
        self.projects.append(project)

    def add_publication(self, publication):
        self.publications.append(publication)

    def add_text_score(self, text_score):
        self.text_scores.append(text_score)

    def add_volunteering(self, volunteer):
        self.volunteering.append(volunteer)

    def add_website(self, website):
        self.websites.append(website)

    def add_post(self, post):
        self.posts.append(post)

    def add_event(self, event):
        self.events.append(event)

    def add_job_offer(self, job_offer):
        self.job_offers.append(job_offer)

    def get_unscraped_results(self):
        return self.search_results.filter(SearchResultPerson.scraped == False).all()

    def are_friends(self, other_user):
        return any(other_user.id == friend.other_party().user.id for friend in self.friends)

    def can_send_request(self, to_user):
        if self.public_id == to_user.public_id:
            # can't send request to yourself
            return False

        # check if other user's `id` exist in send_requests
        if self.sent_requests and any(to_user.id == user_request.to_user_id for user_request in self.sent_requests):
            # already sent
            return False

        return True

    def has_received_in_request_already(self, other_user):
        """ Check if user to request to, has sent in the request already """
        if self.received_requests and any(other_user.id == user_request.from_user_id for user_request in self.received_requests):
            # already received
            return True

        return False

    def to_dict(self):
        data = {
            'public_id': self.public_id,
            'name': self.name,
            'url': self.url,
            'image': self.image,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'connections': self.connections,
            'school': self.school,
            'headline': self.headline,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

        return data

    def from_dict(self, data):
        for field in ['name', 'url', 'image', 'email', 'phone', 'location', 'headline', 'connections', 'school', 'signedup']:
            if field in data:
                setattr(self, field, data[field])

    # method tells Python how to print objects of this class

    def __repr__(self):
        return '<User {}>'.format(self.id)
