-- SQLite schema created automatically by database.init_db().

CREATE TABLE access_codes (
                    user_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

CREATE TABLE preference_profiles (
                user_id TEXT PRIMARY KEY
            );

CREATE TABLE preferences (
                user_id TEXT NOT NULL,
                book_id INTEGER NOT NULL,
                PRIMARY KEY(user_id, book_id)
            );

CREATE TABLE reading_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    book_id INTEGER NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, status TEXT NOT NULL DEFAULT 'planned',
                    UNIQUE(user_id, book_id)
                );
