import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS channels (
    channel_id TEXT PRIMARY KEY,
    channel_name TEXT,
    subscriber_count INTEGER,
    total_views INTEGER,
    video_count INTEGER,
    last_fetched TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS videos (
    video_id TEXT PRIMARY KEY,
    channel_id TEXT,
    title TEXT,
    publish_date TEXT,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS video_stats (
    video_id TEXT,
    fetched_date TEXT,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    FOREIGN KEY (video_id) REFERENCES videos(video_id)
)
""")

conn.commit()
conn.close()

print("Database initialized successfully!")