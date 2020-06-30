from flask import request
from celery import chain

from app.tasks import scrape_and_store_user, search_and_store_results, scrape_search_result_profiles
from app.service.user_service import get_current_user_by_url, get_current_user_by_id
from .errors import error_response, success_response
from app.utils.scrape_util import normalize_url
from .token import token_auth
from app.extensions import db
from app.api import bp


@bp.route('/api/v1/linkedin/signup', methods=['POST'])
def signup_with_linkedin():
    """
    1. Get user url from LinkedIn v1 API
    or
    Get `linkedin_url` from request
    2. Probably requires setting a password
    """
    request_data = request.get_json()
    if not request_data or not "url" in request_data:
        return error_response(400, 'missing url field in request')
    user_url = request_data["url"]

    try:
        user_url = normalize_url(user_url)
        user = get_current_user_by_url(user_url)
        """
        This block handles the user signup case when
        a user who is recommended to another user, exist in database
        but is not signed up, decided to sign up
        """
        user_exist = False
        skip_signup = False
        if user:
            user_exist = True
            if not user.signedup:
                skip_signup = True
        if user_exist and not skip_signup:
            return error_response(409, 'User already exists. Please Log in.')

        task = None
        if not skip_signup:
            """
            Chained Tasks
            Callback executes another celery task with result from first task,
            """
            task = chain(
                scrape_and_store_user.s(user_url),
                search_and_store_results.s(),
                scrape_search_result_profiles.s()
            ).apply_async(countdown=20)  # ToDo: save to a particular queue
        else:
            """
            User is not signed up but exists in database
            Run only the rest of queries
            """
            # set signedup to True
            user.set_signedup()
            db.session.commit()

            task = chain(
                search_and_store_results.s(user.public_id),
                scrape_search_result_profiles.s()
            ).apply_async(countdown=20)  # ToDo: save to a particular queue

        return success_response(201,
                                message='Registration Task {0} {1} for {2}'.format(task.id, task.state, user_url))
    except Exception as e:
        return error_response(500, 'Something went wrong!')


@bp.route('/api/v1/search', methods=['GET'])
@token_auth.login_required
def search():
    try:
        current_user = token_auth.current_user()

        task = search_and_store_results.apply_async(
            args=[current_user.public_id], countdown=20)  # ToDo: save to a particular queue

        return success_response(201,
                                message='Matching Task {0} {1} for {2}'.format(task.id, task.state, current_user.url))
    except Exception as e:
        return error_response(500, 'Something went wrong!')


@bp.route('/api/v1/scrape_user_search_results', methods=['GET'])
@token_auth.login_required
def scrape_user_search_results():
    try:
        current_user = token_auth.current_user()

        task = scrape_search_result_profiles.apply_async(
            args=[current_user.public_id], countdown=20)

        return success_response(201,
                                message='Retrieving Task {0} {1} for {2}'.format(task.id, task.state, current_user.url))
    except Exception as e:
        return error_response(500, 'Something went wrong!')
