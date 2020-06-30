from cloudinary.uploader import upload
from sqlalchemy.exc import SQLAlchemyError
from flask import request
from celery import chain


from app.service.user_service import save_user, get_current_user_by_url, get_current_user_by_id, get_full_user, get_search_results, get_all_user_recommendations, normalize_new_user_data
from app.tasks import search_and_store_results, scrape_search_result_profiles
from app.service.user_match_service import add_friend_request, get_friends
from app.service.job_offer_service import save_job_offer, get_job_offers
from app.service.event_service import save_event, get_events
from app.service.post_service import save_post, get_posts
from .errors import success_response, error_response
from app.utils.fs import get_cloudinary_user_folder
from app.utils.token_util import encode_auth_token
from app.utils.scrape_util import normalize_url
from .token import token_auth
from app.extensions import db
from app.models import User
from app.api import bp


@bp.route('/api/v1/auth/signup', methods=['POST'])
def user_signup():
    """
    Register a normal user

    There will be no url field,
    so replace it with the email as a workaround(for the primary key)
    """
    request_data = request.get_json()
    if not request_data or not "name" in request_data or not "email" in request_data or not "password" in request_data or not "phone" in request_data or not "headline" in request_data or not "location" in request_data or not "skills" in request_data:
        return error_response(400, 'Invalid data supplied')

    try:
        user = get_current_user_by_url(request_data["email"])
        if user:
            return error_response(409, 'User already exists. Please Log in.')

        new_user = normalize_new_user_data(request_data)
        user_public_id = save_user(new_user, True)
        current_user = get_current_user_by_id(user_public_id)
        current_user.set_password(request_data["password"])
        db.session.commit()

        task = chain(
            search_and_store_results.s(user_public_id),
            scrape_search_result_profiles.s()
        ).apply_async(countdown=5)  # ToDo: save to a particular queue

        auth_token = encode_auth_token(
            current_user.public_id.hex)  # uuid to string
        if not auth_token:
            return error_response(500, 'Something went wrong!')

        return {
            'response': {
                'statusCode': 201,
                'statusText': 'OK'
            },
            'data': {
                'status': True,
                'message': 'Successfully registered.',
                'token': auth_token
            }
        }
    except SQLAlchemyError as e:
        db.session.rollback()
    except Exception as e:
        pass

    return error_response(500, 'Failed to signup. Try again later.')


@bp.route('/api/v1/auth/signin', methods=['POST'])
def user_signin():
    request_data = request.get_json()
    if not request_data or not "email" in request_data or not "password" in request_data:
        return error_response(400, 'Invalid data supplied')

    try:
        user = get_current_user_by_url(request_data["email"])
        if not user or not user.check_password(request_data["password"]):
            return error_response(401, 'Invalid email or password')

        auth_token = encode_auth_token(user.public_id.hex)  # uuid to string
        if not auth_token:
            return error_response(500, 'Something went wrong!')

        return {
            'response': {
                'statusCode': 200,
                'statusText': 'OK'
            },
            'data': {
                'status': True,
                'message': 'Successfully logged in.',
                'token': auth_token
            }
        }
    except Exception as e:
        pass

    return error_response(500, 'Failed to login. Try again later.')


@bp.route('/api/v1/user/upload_profile_picture', methods=['POST'])
@token_auth.login_required
def upload_profile_picture():
    file_to_upload = request.files['image']
    if not file_to_upload:
        return error_response(400, 'Missing image file')

    try:
        current_user = token_auth.current_user()
        # upload image to cloudinary service
        upload_result = upload(file_to_upload,
                               folder="{0}/profiles".format(
                                   get_cloudinary_user_folder(current_user.url)),
                               overwrite=False)
        current_user.change_profile_image(upload_result["secure_url"])
        db.session.commit()

        return success_response(201, 'Profile picture updated successfully')
    except Exception as e:
        pass

    return error_response(500, 'Failed to change profile picture. Try again later.')


@bp.route('/api/v1/get_user', methods=['GET'])
@token_auth.login_required
def get_user():
    try:
        current_user = token_auth.current_user()

        return success_response(200, data=get_full_user(current_user))
    except Exception as e:
        pass

    return error_response(500, 'Something went wrong. Try again later.')


@bp.route('/api/v1/get_users', methods=['GET'])
@token_auth.login_required
def get_users():
    # ToDo: check if admin email with jwt auth
    try:
        result = User.query.all()
        users = list(map(lambda x: x.to_dict(), result))

        return success_response(200,
                                data={
                                    'data': users,
                                    'total': len(users)
                                })
    except Exception as e:
        pass

    return error_response(500, 'Something went wrong. Try again later.')


@bp.route('/api/v1/get_user_search_results', methods=['GET'])
@token_auth.login_required
def get_user_search_results():
    try:
        current_user = token_auth.current_user()
        result = get_search_results(current_user.search_results)

        return success_response(200,
                                data={
                                    'data': result,
                                    'total': len(result)
                                })
    except Exception as e:
        pass

    return error_response(500, 'Something went wrong. Try again later.')


@bp.route('/api/v1/get_user_recommendations', methods=['GET'])
@token_auth.login_required
def get_user_recommendations():
    # ToDo: filter if person is a friend or already requested to
    try:
        current_user = token_auth.current_user()
        result = get_all_user_recommendations(current_user.recommended_list)

        return success_response(200,
                                data={
                                    'data': result,
                                    'total': len(result)
                                })
    except Exception as e:
        pass

    return error_response(500, 'Something went wrong. Try again later.')


@bp.route('/api/v1/post/new', methods=['POST'])
@token_auth.login_required
def add_new_post():
    # type is `form-data`
    file_to_upload = request.files['image']
    request_data = request.form

    if not request_data or not "body" in request_data or not file_to_upload:
        return error_response(400, 'Invalid data supplied')

    try:
        current_user = token_auth.current_user()
        # upload image to cloudinary service
        upload_result = upload(file_to_upload,
                               folder="{0}/posts".format(get_cloudinary_user_folder(
                                   current_user.url)),
                               overwrite=False)
        new_post = {'body': request_data["body"],
                    'image': upload_result["secure_url"],
                    'user_id': current_user.id}
        post_id = save_post(new_post, current_user)

        return success_response(201,
                                message='Posted successfully')
    except SQLAlchemyError as e:
        db.session.rollback()
    except Exception as e:
        pass

    return error_response(500, 'Error creating new post!')


@bp.route('/api/v1/user/posts', methods=['GET'])
@token_auth.login_required
def get_user_posts():
    try:
        current_user = token_auth.current_user()
        posts = get_posts(current_user.posts)

        return success_response(200,
                                data={
                                    'data': posts,
                                    'total': len(posts)
                                })
    except Exception as e:
        pass

    return error_response(500, 'Error retrieving user posts!')


@bp.route('/api/v1/timeline/posts', methods=['POST'])
@token_auth.login_required
def get_user_timeline_latest_posts():
    """ Get Posts to show on timeline """
    try:
        current_user = token_auth.current_user()

        return success_response(200, 'success')
    except Exception as e:
        pass

    return error_response(500, 'Error retrieving user posts!')


@bp.route('/api/v1/event/new', methods=['POST'])
@token_auth.login_required
def add_new_event():
    request_data = request.get_json()

    if not request_data or not "title" in request_data or not "venue" in request_data or not "location" in request_data or not "description" in request_data or not "start_date" in request_data or not "start_time" in request_data or not "end_date" in request_data or not "end_time" in request_data:
        return error_response(400, 'Invalid data supplied')

    try:
        current_user = token_auth.current_user()
        new_event = {
            'user_id': current_user.id,
            'title': request_data["title"],
            'venue': request_data["venue"],
            'location': request_data["location"],
            'description': request_data["description"],
            # convert to datetime format
            'starts_at': "{0} {1}".format(request_data["start_date"], request_data["start_time"]),
            # convert to datetime format
            'ends_at': "{0} {1}".format(request_data["end_date"], request_data["end_time"]),
        }
        event_id = save_event(new_event, current_user)

        return success_response(201, message='Event scheduled successfully')
    except SQLAlchemyError as e:
        db.session.rollback()
    except Exception as e:
        pass

    return error_response(500, 'Error creating new event!')


@bp.route('/api/v1/user/events', methods=['GET'])
@token_auth.login_required
def get_user_events():
    try:
        current_user = token_auth.current_user()
        events = get_events(current_user.events)

        return success_response(200,
                                data={
                                    'data': events,
                                    'total': len(events)
                                })
    except Exception as e:
        pass

    return error_response(500, 'Error retrieving user events!')


@bp.route('/api/v1/job_offer/new', methods=['POST'])
@token_auth.login_required
def add_new_job_offer():
    request_data = request.get_json()

    if not request_data or not "title" in request_data or not "venue" in request_data or not "location" in request_data or not "description" in request_data or not "contact" in request_data or not "start_date" in request_data:
        return error_response(400, 'Invalid data supplied')

    try:
        current_user = token_auth.current_user()
        new_job_offer = {
            'user_id': current_user.id,
            'title': request_data["title"],
            'venue': request_data["venue"],
            'location': request_data["location"],
            'description': request_data["description"],
            'contact': request_data["contact"],
            'starts_at': request_data["start_date"],
        }
        job_offer_id = save_job_offer(new_job_offer, current_user)

        return success_response(201, message='Job offer created successfully')
    except SQLAlchemyError as e:
        db.session.rollback()
    except Exception as e:
        pass

    return error_response(500, 'Error creating new job offer!')


@bp.route('/api/v1/user/job_offers', methods=['GET'])
@token_auth.login_required
def get_user_job_offers():
    try:
        current_user = token_auth.current_user()
        job_offers = get_job_offers(current_user.job_offers)

        return success_response(200,
                                data={
                                    'data': job_offers,
                                    'total': len(job_offers)
                                })
    except Exception as e:
        pass

    return error_response(500, 'Error retrieving user job offers!')


@bp.route('/api/v1/user/match_request', methods=['POST'])
@token_auth.login_required
def handle_match_request():
    request_data = request.get_json()

    if not request_data or not "match_user_public_id" in request_data or not "status" in request_data or not (request_data["status"] == 0 or request_data["status"] == 1):
        return error_response(400, 'Invalid data supplied')

    try:
        current_user = token_auth.current_user()
        user_to_match = get_current_user_by_id(
            request_data["match_user_public_id"])

        if not user_to_match:
            return error_response(404, 'No such user to send request to!')

        # if user wants to meet -> `pending` else `rejected`
        status_text = "pending" if request_data["status"] == 1 else "rejected"

        # True if matched, False if pending, None if request is not possible to process
        res = add_friend_request(
            current_user, other_user=user_to_match, status_text=status_text)

        if res is not None:
            if res:
                return success_response(200,
                                        message='Matching successful',
                                        data={
                                            'match': True
                                        })

            return success_response(201,
                                    message='Matching in progress',
                                    data={
                                        'match': False
                                    })

        return error_response(500,
                              message='Request is either pending or already accepted')

    except SQLAlchemyError as e:
        db.session.rollback()
    except Exception as e:
        pass

    return error_response(500, 'Error creating new match request!')


@bp.route('/api/v1/user/friends', methods=['GET'])
@token_auth.login_required
def get_user_friends():
    try:
        current_user = token_auth.current_user()
        friends = get_friends(current_user.friends)

        return success_response(200,
                                data={
                                    'data': friends,
                                    'total': len(friends)
                                })
    except Exception as e:
        pass

    return error_response(500, 'Error retrieving user friends!')
