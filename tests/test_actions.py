import psycopg2
import pytest

from app.actions import add_comment, create_post, follow_user, unfollow_user
from app.database import get_connection, release_connection


def fetch_one(sql, params):
    """Run one SELECT and return the first row (or None)."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()
    finally:
        connection.rollback()  # end the read, so the connection is clean for the next user
        release_connection(connection)


def get_counts(user_id):
    """Return (followers_count, following_count) for a user."""
    return fetch_one(
        "SELECT followers_count, following_count FROM users WHERE user_id = %s;",
        (user_id,),
    )


def test_create_user_returns_an_id(make_user):
    user_id = make_user()
    assert isinstance(user_id, int)


def test_new_user_has_zero_counts(make_user):
    user_id = make_user()
    assert get_counts(user_id) == (0, 0)


def test_create_post_saves_content_and_metadata(make_user):
    user_id = make_user()
    post_id = create_post(user_id, "Hello test", {"tags": ["test"]})

    row = fetch_one("SELECT user_id, content, metadata FROM posts WHERE post_id = %s;", (post_id,))
    assert row == (user_id, "Hello test", {"tags": ["test"]})


def test_add_comment_saves_comment(make_user):
    author = make_user()
    commenter = make_user()
    post_id = create_post(author, "A post")

    comment_id = add_comment(post_id, commenter, "Nice post")

    row = fetch_one("SELECT post_id, user_id, content FROM comments WHERE comment_id = %s;", (comment_id,))
    assert row == (post_id, commenter, "Nice post")


def test_follow_updates_counts(make_user):
    alice = make_user()
    bob = make_user()

    follow_user(alice, bob)

    assert get_counts(alice) == (0, 1)  # alice follows 1 person
    assert get_counts(bob) == (1, 0)    # bob has 1 follower


def test_follow_twice_fails_and_counts_stay_the_same(make_user):
    alice = make_user()
    bob = make_user()
    follow_user(alice, bob)

    # The second follow breaks the primary key, so the whole transaction is rolled back
    with pytest.raises(psycopg2.IntegrityError):
        follow_user(alice, bob)

    assert get_counts(alice) == (0, 1)
    assert get_counts(bob) == (1, 0)


def test_unfollow_puts_counts_back(make_user):
    alice = make_user()
    bob = make_user()
    follow_user(alice, bob)

    unfollow_user(alice, bob)

    assert get_counts(alice) == (0, 0)
    assert get_counts(bob) == (0, 0)


def test_unfollow_without_follow_changes_nothing(make_user):
    alice = make_user()
    bob = make_user()

    unfollow_user(alice, bob)

    assert get_counts(alice) == (0, 0)
    assert get_counts(bob) == (0, 0)
