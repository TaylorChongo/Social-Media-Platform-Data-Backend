# Social Media Platform Data Backend

The data backend for a simple social media app. Users can write posts, comment on posts, and follow each other.

## Tech Stack

- **PostgreSQL**: main database (users, posts, comments, followers)
- **Python** with `psycopg2`: scripts that talk to the database
- **Redis**: caching user timelines
- **MongoDB**: activity logs (likes, follows, ...)

## Database Design

```mermaid
erDiagram
    USERS ||--o{ POSTS : writes
    USERS ||--o{ COMMENTS : writes
    POSTS ||--o{ COMMENTS : has
    USERS ||--o{ FOLLOWERS : follows
    USERS ||--o{ FOLLOWERS : "is followed by"

    USERS {
        int user_id PK
        string username
        string email
        timestamp created_at
    }

    POSTS {
        int post_id PK
        int user_id FK
        string content
        jsonb metadata
        timestamp created_at
    }

    COMMENTS {
        int comment_id PK
        int post_id FK
        int user_id FK
        string content
        timestamp created_at
    }

    FOLLOWERS {
        int follower_id PK, FK
        int followee_id PK, FK
        timestamp created_at
    }
```

## Project Structure

```
social-media-backend/
├── db/
│   ├── schema.sql      # creates the 4 tables
│   └── test_data.sql   # a few sample rows
├── docs/
│   └── er_diagram.md   # ER diagram of the database
├── .gitignore
└── README.md
```

## Getting Started

1. Clone the repository and open the folder.
2. Create a virtual environment:
   ```
   python -m venv .venv
   ```
3. Activate it (Windows):
   ```
   .venv\Scripts\activate
   ```
4. Create the database (inside `psql -U postgres`):
   ```sql
   CREATE DATABASE social_media;
   ```
5. Create the tables, then add the sample data:
   ```
   psql -U postgres -d social_media -f db/schema.sql
   psql -U postgres -d social_media -f db/test_data.sql
   ```

## Progress

- [x] Day 1: Database schema design and setup
- [ ] Day 2: Core user actions with Python transactions
- [ ] Day 3: Redis caching and MongoDB logging
- [ ] Day 4: Feed query building and optimization
