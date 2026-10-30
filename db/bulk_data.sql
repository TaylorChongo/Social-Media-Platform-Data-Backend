-- Lots of fake rows, so we can measure how fast queries are

-- 1000 users: user1, user2, ... user1000
INSERT INTO users (username, email)
SELECT 'user' || n, 'user' || n || '@mail.com'
FROM generate_series(1, 1000) AS n;

-- 100 posts for every user, spread over the last year
INSERT INTO posts (user_id, content, created_at)
SELECT u.user_id, 'Post number ' || n, NOW() - random() * INTERVAL '365 days'
FROM users u, generate_series(1, 100) AS n;

-- Every user follows the next 50 users (by user_id)
INSERT INTO followers (follower_id, followee_id)
SELECT a.user_id, b.user_id
FROM users a
JOIN users b ON b.user_id > a.user_id AND b.user_id <= a.user_id + 50
ON CONFLICT DO NOTHING;

-- Make the counts match the follows above
UPDATE users SET
    followers_count = (SELECT COUNT(*) FROM followers WHERE followee_id = users.user_id),
    following_count = (SELECT COUNT(*) FROM followers WHERE follower_id = users.user_id);
