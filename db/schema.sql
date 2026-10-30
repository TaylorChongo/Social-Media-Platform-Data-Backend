-- Remove old tables so this file can be run again
DROP TABLE IF EXISTS followers;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

-- Users of the app
CREATE TABLE users (
    user_id    SERIAL PRIMARY KEY,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    email      VARCHAR(100) NOT NULL UNIQUE,
    followers_count INTEGER NOT NULL DEFAULT 0,
    following_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP    DEFAULT NOW()
);

-- Posts written by users
CREATE TABLE posts (
    post_id    SERIAL PRIMARY KEY,
    user_id    INTEGER   NOT NULL REFERENCES users(user_id),
    content    TEXT      NOT NULL,
    metadata   JSONB     DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Speeds up the feed: find a user's posts, already sorted newest first
CREATE INDEX idx_posts_user_created ON posts (user_id, created_at DESC);

-- Comments on posts
CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    post_id    INTEGER   NOT NULL REFERENCES posts(post_id),
    user_id    INTEGER   NOT NULL REFERENCES users(user_id),
    content    TEXT      NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Who follows whom: each row means "follower_id follows followee_id"
CREATE TABLE followers (
    follower_id INTEGER   NOT NULL REFERENCES users(user_id),
    followee_id INTEGER   NOT NULL REFERENCES users(user_id),
    created_at  TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (follower_id, followee_id),
    CHECK (follower_id <> followee_id)
);
