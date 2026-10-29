import json

from database import get_connection, redis_client, release_connection

# How long a cached timeline stays in Redis before it expires
CACHE_SECONDS = 60


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
            "created_at": row[4].isoformat(),  # date as text, so it can be saved as JSON
        })
    return timeline


def get_cached_timeline(user_id):
    """Return the timeline from Redis if it is there, otherwise build and cache it."""
    key = "timeline:" + str(user_id)

    # 1. Try Redis first
    cached = redis_client.get(key)
    if cached is not None:
        return json.loads(cached)

    # 2. Not in Redis: build it from PostgreSQL
    timeline = get_timeline(user_id)

    # 3. Save a copy in Redis that expires after CACHE_SECONDS
    redis_client.set(key, json.dumps(timeline), ex=CACHE_SECONDS)
    return timeline
