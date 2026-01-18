import requests
import sqlite3
import os
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
DB_NAME = "database.db"

if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY not found in .env file")


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


if __name__ == "__main__":
    channel_url = input("Paste YouTube channel link: ").strip()

    channel_id = get_channel_id(channel_url)
    channel_data = get_channel_data(channel_id)
    video_ids = get_recent_videos(channel_id)
    stats = get_video_stats(video_ids)

    save_to_db(channel_data, video_ids, stats)

    print("Analytics saved successfully")