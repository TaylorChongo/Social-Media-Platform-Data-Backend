from database import get_connection, release_connection


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
    return user_id


def create_post(user_id, content):
    """Add a new post for a user and return its post_id."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO posts (user_id, content) VALUES (%s, %s) RETURNING post_id;",
            (user_id, content),
        )
        post_id = cursor.fetchone()[0]
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        release_connection(connection)
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
    return comment_id


def follow_user(follower_id, followee_id):
    """Make follower_id follow followee_id."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO followers (follower_id, followee_id) VALUES (%s, %s);",
            (follower_id, followee_id),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        release_connection(connection)


def unfollow_user(follower_id, followee_id):
    """Make follower_id stop following followee_id."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM followers WHERE follower_id = %s AND followee_id = %s;",
            (follower_id, followee_id),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        release_connection(connection)
