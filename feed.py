import json

from database import get_connection, redis_client, release_connection

# How long a cached timeline stays in Redis before it expires
CACHE_SECONDS = 60


def get_timeline(user_id, limit=20, page=1):
    """Return one page of the newest posts from the people user_id follows."""
    # Page 1 skips 0 posts, page 2 skips 20, page 3 skips 40, ...
    offset = (page - 1) * limit

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
            LIMIT %s OFFSET %s;
            """,
            (user_id, limit, offset),
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


def clear_timeline_cache(user_id):
    """Delete a user's cached timeline so it is rebuilt next time."""
    redis_client.delete("timeline:" + str(user_id))


def clear_follower_timelines(user_id):
    """Delete the cached timelines of everyone who follows user_id."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT follower_id FROM followers WHERE followee_id = %s;",
            (user_id,),
        )
        rows = cursor.fetchall()
    except Exception:
        connection.rollback()
        raise
    finally:
        release_connection(connection)

    for row in rows:
        clear_timeline_cache(row[0])
