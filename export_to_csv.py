import sqlite3
import pandas as pd

conn = sqlite3.connect("database.db")

channels = pd.read_sql("SELECT * FROM channels", conn)
videos = pd.read_sql("SELECT * FROM videos", conn)
stats = pd.read_sql("SELECT * FROM video_stats", conn)

channels.to_csv("channels.csv", index=False)
videos.to_csv("videos.csv", index=False)
stats.to_csv("video_stats.csv", index=False)

conn.close()

print("CSV files exported successfully")