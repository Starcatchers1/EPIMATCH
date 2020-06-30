from flask import Flask

from app.utils.celery_util import init_celery
from app.extensions import db, migrate
from app import models, api, celery
from config import ProdConfig


def create_app(config_object=ProdConfig):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_object)

    init_celery(flask_app, celery)

    register_extensions(flask_app)
    register_blueprints(flask_app)
    register_shellcontext(flask_app)

    return flask_app


def register_extensions(flask_app):
    """Register Flask extensions."""
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)


def register_blueprints(flask_app):
    """Register Flask blueprints."""
    flask_app.register_blueprint(api.bp)


def register_shellcontext(flask_app):
    """Register shell context objects.
       Creates a shell context that adds the database
       instance and models to the shell session
    """
    def make_shell_context():
        """Shell context objects."""
        return {
            'db': db,
            'Job': models.Job,
            'User': models.User,
            'Post': models.Post,
            'Event': models.Event,
            'Honor': models.Honor,
            'Skill': models.Skill,
            'Patent': models.Patent,
            'Course': models.Course,
            'Company': models.Company,
            'Project': models.Project,
            'Website': models.Website,
            'Interest': models.Interest,
            'JobOffer': models.JobOffer,
            'Language': models.Language,
            'TextScore': models.TextScore,
            'Volunteer': models.Volunteer,
            'Education': models.Education,
            'UserMatch': models.UserMatch,
            'Publication': models.Publication,
            'Organization': models.Organization,
            'Certification': models.Certification,
            'UserFriendship': models.UserFriendship,
            'UserRecommendation': models.UserRecommendation,
            'SearchResultPerson': models.SearchResultPerson,
            'UserSkillAssociation': models.UserSkillAssociation,
            'UserFriendshipRequest': models.UserFriendshipRequest,
            'UserInterestAssociation': models.UserInterestAssociation,
            'UserEducationAssociation': models.UserEducationAssociation,
            'SearchResultPersonAssociation': models.SearchResultPersonAssociation
        }

    flask_app.shell_context_processor(make_shell_context)
