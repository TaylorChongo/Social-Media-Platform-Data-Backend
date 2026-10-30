from app.actions import add_comment, create_post, follow_user, like_post, unfollow_user
from app.activity import get_user_activity


def get_actions(user_id):
    """Return just the action names from a user's activity log, e.g. ["post", "signup"]."""
    return [activity["action"] for activity in get_user_activity(user_id)]


def test_signup_is_logged(make_user):
    user_id = make_user()
    assert get_actions(user_id) == ["signup"]


def test_post_and_comment_are_logged(make_user):
    user_id = make_user()
    post_id = create_post(user_id, "A post")
    add_comment(post_id, user_id, "My own comment")

    actions = get_actions(user_id)

    assert "post" in actions
    assert "comment" in actions


def test_follow_and_unfollow_are_logged_with_details(make_user):
    alice = make_user()
    bob = make_user()
    follow_user(alice, bob)
    unfollow_user(alice, bob)

    activities = get_user_activity(alice)

    follow = [a for a in activities if a["action"] == "follow"][0]
    assert follow["details"] == {"followee_id": bob}
    assert "unfollow" in get_actions(alice)


def test_like_is_logged(make_user):
    alice = make_user()
    post_id = create_post(alice, "Like me")

    like_post(alice, post_id)

    activities = get_user_activity(alice)
    like = [a for a in activities if a["action"] == "like"][0]
    assert like["details"] == {"post_id": post_id}
