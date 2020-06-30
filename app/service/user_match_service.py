from ..models import UserFriendshipRequest, UserMatch, UserFriendship
from app.extensions import db


def add_friendship(user1, user2):
    """ Create a User -> UserMatch relation and then append it to UserRelationship """
    pl = UserFriendship()
    pl.parties.append(UserMatch(user=user1))
    pl.parties.append(UserMatch(user=user2))

    return pl


def add_friend_request(current_user, other_user, status_text):
    """ Create a friendship request """
    if current_user.public_id == other_user.public_id:
        # Users cannot be friends with themselves
        return None

    if current_user.are_friends(other_user):
        # Users are already friends
        return None

    if not current_user.can_send_request(other_user):
        # Request already sent
        return None

    if current_user.has_received_in_request_already(other_user):
        all_received_requests = current_user.received_requests
        existing_request = [
            request for request in all_received_requests if request.from_user_id == other_user.id][0]
        # If existing is pending and new user wan't to meet,
        # add friends with new user and delete request
        if existing_request.status == 'pending':
            if status_text == "rejected":
                # Update request status to `rejected`
                existing_request.reject_request()
                db.session.commit()
                return False

            # add new friendship between users
            add_friendship(current_user, other_user)
            # delete request
            db.session.delete(existing_request)
            db.session.commit()
            return True

        return None

    # send a new request
    new_friendship_request = UserFriendshipRequest()
    data = {
        'to_user_id': other_user.public_id,
        'to_user': other_user,
        'from_user_id': current_user.public_id,
        'from_user': current_user,
        'status': status_text
    }
    new_friendship_request.from_dict(data)
    db.session.add(new_friendship_request)
    db.session.commit()

    return False


def get_friends(friends):
    def get_friend(self_friend_obj):
        other_user_friend = self_friend_obj.other_party()
        other_user = other_user_friend.user

        return other_user.to_dict()

    return list(map(get_friend, friends))
