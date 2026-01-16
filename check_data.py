import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

print("Channels:")
for row in cur.execute("SELECT * FROM channels"):
    print(row)

print("\nVideo stats:")
for row in cur.execute("SELECT * FROM video_stats LIMIT 5"):
    print(row)

conn.close()
