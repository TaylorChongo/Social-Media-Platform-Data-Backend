from psycopg2.extras import Json

from activity import log_activity
from database import get_connection, release_connection
from feed import clear_follower_timelines, clear_timeline_cache


def create_user(username, email):
    """Add a new user and return their user_id."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING user_id;",
            (username, email),
        )
        user_id = cursor.fetchone()[0]
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        release_connection(connection)
    log_activity(user_id, "signup", {"username": username})
    return user_id


def create_post(user_id, content, metadata=None):
    """Add a new post for a user and return its post_id.

    metadata is an optional dictionary, e.g. {"tags": ["sql"], "location": "Accra"}
    """
    if metadata is None:
        metadata = {}
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO posts (user_id, content, metadata) VALUES (%s, %s, %s) RETURNING post_id;",
            (user_id, content, Json(metadata)),
        )
        post_id = cursor.fetchone()[0]
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        release_connection(connection)
    # The author's followers now have an out-of-date cached timeline
    clear_follower_timelines(user_id)
    log_activity(user_id, "post", {"post_id": post_id})
    return post_id


def add_comment(post_id, user_id, content):
    """Add a comment by a user on a post and return its comment_id."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO comments (post_id, user_id, content) VALUES (%s, %s, %s) RETURNING comment_id;",
            (post_id, user_id, content),
        )
        comment_id = cursor.fetchone()[0]
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        release_connection(connection)
    log_activity(user_id, "comment", {"post_id": post_id, "comment_id": comment_id})
    return comment_id


def follow_user(follower_id, followee_id):
    """Make follower_id follow followee_id (all steps happen, or none)."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        # Step 1: add the follow
        cursor.execute(
            "INSERT INTO followers (follower_id, followee_id) VALUES (%s, %s);",
            (follower_id, followee_id),
        )
        # Step 2: the follower now follows one more person
        cursor.execute(
            "UPDATE users SET following_count = following_count + 1 WHERE user_id = %s;",
            (follower_id,),
        )
        # Step 3: the followee now has one more follower
        cursor.execute(
            "UPDATE users SET followers_count = followers_count + 1 WHERE user_id = %s;",
            (followee_id,),
        )
        # All steps worked: save them together
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        release_connection(connection)
    # The follower's timeline now includes new people
    clear_timeline_cache(follower_id)
    log_activity(follower_id, "follow", {"followee_id": followee_id})


def unfollow_user(follower_id, followee_id):
    """Make follower_id stop following followee_id (all steps happen, or none)."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        # Step 1: remove the follow
        cursor.execute(
            "DELETE FROM followers WHERE follower_id = %s AND followee_id = %s;",
            (follower_id, followee_id),
        )
        # Only change the counts if a follow was really removed
        removed = cursor.rowcount == 1
        if removed:
            # Step 2: the follower now follows one less person
            cursor.execute(
                "UPDATE users SET following_count = following_count - 1 WHERE user_id = %s;",
                (follower_id,),
            )
            # Step 3: the followee now has one less follower
            cursor.execute(
                "UPDATE users SET followers_count = followers_count - 1 WHERE user_id = %s;",
                (followee_id,),
            )
        # All steps worked: save them together
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        release_connection(connection)
    if removed:
        # The follower's timeline no longer includes this person
        clear_timeline_cache(follower_id)
        log_activity(follower_id, "unfollow", {"followee_id": followee_id})


def like_post(user_id, post_id):
    """Record that a user liked a post (likes are only stored in MongoDB)."""
    log_activity(user_id, "like", {"post_id": post_id})
