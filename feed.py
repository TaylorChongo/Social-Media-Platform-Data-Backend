from database import get_connection, release_connection


def get_timeline(user_id, limit=20):
    """Return the newest posts from the people user_id follows."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT p.post_id, u.username, p.content, p.metadata, p.created_at
            FROM followers f
            JOIN posts p ON p.user_id = f.followee_id
            JOIN users u ON u.user_id = p.user_id
            WHERE f.follower_id = %s
            ORDER BY p.created_at DESC
            LIMIT %s;
            """,
            (user_id, limit),
        )
        rows = cursor.fetchall()
    except Exception:
        connection.rollback()
        raise
    finally:
        release_connection(connection)

    # Turn each row into a dictionary so it is easy to read (and to cache later)
    timeline = []
    for row in rows:
        timeline.append({
            "post_id": row[0],
            "username": row[1],
            "content": row[2],
            "metadata": row[3],
            "created_at": row[4],
        })
    return timeline
