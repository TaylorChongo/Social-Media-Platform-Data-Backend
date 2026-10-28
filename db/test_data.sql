-- A few sample rows to check that the tables work

-- 3 users (they get user_id 1, 2, 3)
INSERT INTO users (username, email) VALUES ('ama', 'ama@mail.com');
INSERT INTO users (username, email) VALUES ('kofi', 'kofi@mail.com');
INSERT INTO users (username, email) VALUES ('esi', 'esi@mail.com');

-- Posts (they get post_id 1, 2, 3)
INSERT INTO posts (user_id, content, metadata)
VALUES (1, 'Hello everyone!', '{"tags": ["intro"], "location": "Accra"}');

INSERT INTO posts (user_id, content, metadata)
VALUES (2, 'Learning SQL today', '{"tags": ["sql", "postgres"]}');

INSERT INTO posts (user_id, content)
VALUES (3, 'Good morning');

-- Comments
INSERT INTO comments (post_id, user_id, content) VALUES (1, 2, 'Welcome Ama!');
INSERT INTO comments (post_id, user_id, content) VALUES (2, 1, 'Nice, keep going');

-- Follows
INSERT INTO followers (follower_id, followee_id) VALUES (1, 2);  -- ama follows kofi
INSERT INTO followers (follower_id, followee_id) VALUES (1, 3);  -- ama follows esi
INSERT INTO followers (follower_id, followee_id) VALUES (2, 1);  -- kofi follows ama

-- Counts that match the follows above
UPDATE users SET followers_count = 1, following_count = 2 WHERE user_id = 1;  -- ama
UPDATE users SET followers_count = 1, following_count = 1 WHERE user_id = 2;  -- kofi
UPDATE users SET followers_count = 1, following_count = 0 WHERE user_id = 3;  -- esi
