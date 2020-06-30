from app.extensions import db
from ..models import Post


def save_post(post_data, user):
    post = Post()
    post.from_dict(post_data)
    db.session.add(post)
    user.add_post(post)
    db.session.commit()

    return post.public_id


def get_posts(posts):
    return list(map(lambda x: x.to_dict(), posts))
