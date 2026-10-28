from database import get_connection


def create_user(username, email):
    """Add a new user and return their user_id."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING user_id;",
        (username, email),
    )
    user_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    connection.close()
    return user_id


def create_post(user_id, content):
    """Add a new post for a user and return its post_id."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO posts (user_id, content) VALUES (%s, %s) RETURNING post_id;",
        (user_id, content),
    )
    post_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    connection.close()
    return post_id
