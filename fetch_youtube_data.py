import requests
import sqlite3
import os
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
DB_NAME = "database.db"

def get_all_tracked_channels():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute("SELECT channel_id FROM channels")
        rows = cur.fetchall()
        return [row[0] for row in rows]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()

def get_channel_id(channel_url):
    path = urlparse(channel_url).path.strip("/")
    if path.startswith("channel/"):
        return path.split("/")[-1]
    query = path.replace("@", "").replace("c/", "")
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "channel",
        "maxResults": 1,
        "key": API_KEY
    }
    data = requests.get(url, params=params).json()
    return data["items"][0]["snippet"]["channelId"]

def get_channel_data(channel_id):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,statistics",
        "id": channel_id,
        "key": API_KEY
    }
    item = requests.get(url, params=params).json()["items"][0]
    return (
        channel_id,
        item["snippet"]["title"],
        int(item["statistics"]["subscriberCount"]),
        int(item["statistics"]["viewCount"]),
        int(item["statistics"]["videoCount"]),
        datetime.now().strftime("%Y-%m-%d")
    )

def get_recent_videos(channel_id):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "id",
        "channelId": channel_id,
        "maxResults": 20,
        "order": "date",
        "type": "video",
        "key": API_KEY
    }
    return [
        item["id"]["videoId"]
        for item in requests.get(url, params=params).json()["items"]
    ]

def get_video_stats(video_ids):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "statistics",
        "id": ",".join(video_ids),
        "key": API_KEY
    }
    items = requests.get(url, params=params).json()["items"]
    today = datetime.now().strftime("%Y-%m-%d")
    return [
        (
            v["id"],
            today,
            int(v["statistics"].get("viewCount", 0)),
            int(v["statistics"].get("likeCount", 0)),
            int(v["statistics"].get("commentCount", 0))
        )
        for v in items
    ]

def save_to_db(channel, video_ids, stats):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO channels VALUES (?, ?, ?, ?, ?, ?)",
        channel
    )
    for vid in video_ids:
        cur.execute(
            "INSERT OR IGNORE INTO videos VALUES (?, ?, '', '')",
            (vid, channel[0])
        )
    for s in stats:
        cur.execute(
            "INSERT INTO video_stats VALUES (?, ?, ?, ?, ?)",
            s
        )
    conn.commit()
    conn.close()

def process_channels(channel_ids):
    for c_id in channel_ids:
        try:
            channel_data = get_channel_data(c_id)
            video_ids = get_recent_videos(c_id)
            stats = get_video_stats(video_ids)
            save_to_db(channel_data, video_ids, stats)
            print(f"Updated: {channel_data[1]}")
        except Exception as e:
            print(f"Error {c_id}: {e}")

if __name__ == "__main__":
    print("YouTube Analytics Tracker")
    print("1. Refresh existing channels")
    print("2. Add a new channel")
    choice = input("Select an option (1 or 2): ").strip()

    if choice == "1":
        tracked_ids = get_all_tracked_channels()
        if not tracked_ids:
            print("No channels found in database. Add one first.")
        else:
            process_channels(tracked_ids)
    
    elif choice == "2":
        channel_url = input("Paste YouTube channel link: ").strip()
        channel_id = get_channel_id(channel_url)
        process_channels([channel_id])
        print("New channel added and stats fetched.")
    
    else:
        print("Invalid choice.")