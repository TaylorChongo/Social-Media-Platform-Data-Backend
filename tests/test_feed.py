from app.actions import create_post, follow_user
from app.database import redis_client
from app.feed import get_cached_timeline, get_timeline


def cache_key(user_id):
    return "timeline:" + str(user_id)


def test_timeline_only_shows_followed_users(make_user):
    alice = make_user()
    bob = make_user()
    carol = make_user()
    follow_user(alice, bob)  # alice follows bob, but not carol
    create_post(bob, "From bob")
    create_post(carol, "From carol")

    timeline = get_timeline(alice)

    contents = [post["content"] for post in timeline]
    assert contents == ["From bob"]


def test_timeline_is_newest_first(make_user):
    alice = make_user()
    bob = make_user()
    follow_user(alice, bob)
    create_post(bob, "Older post")
    create_post(bob, "Newer post")

    timeline = get_timeline(alice)

    assert timeline[0]["content"] == "Newer post"
    assert timeline[1]["content"] == "Older post"


def test_timeline_pages_do_not_repeat_posts(make_user):
    alice = make_user()
    bob = make_user()
    follow_user(alice, bob)
    create_post(bob, "Post 1")
    create_post(bob, "Post 2")
    create_post(bob, "Post 3")

    page1 = get_timeline(alice, limit=2, page=1)
    page2 = get_timeline(alice, limit=2, page=2)

    assert len(page1) == 2
    assert len(page2) == 1
    assert page2[0]["content"] == "Post 1"  # the oldest post is on the last page


def test_cached_timeline_is_saved_in_redis(make_user):
    alice = make_user()

    get_cached_timeline(alice)

    assert redis_client.get(cache_key(alice)) is not None


def test_new_post_clears_followers_cache(make_user):
    alice = make_user()
    bob = make_user()
    follow_user(alice, bob)
    get_cached_timeline(alice)  # fills the cache

    create_post(bob, "Fresh post")

    assert redis_client.get(cache_key(alice)) is None
    assert get_cached_timeline(alice)[0]["content"] == "Fresh post"


def test_follow_clears_followers_cache(make_user):
    alice = make_user()
    bob = make_user()
    get_cached_timeline(alice)  # fills the cache

    follow_user(alice, bob)

    assert redis_client.get(cache_key(alice)) is None
