"""
Video Tracker: Keeps track of which videos have already been processed.
This prevents sending duplicate articles for the same video.
"""

import os
import json
from datetime import datetime

# File to store processed video IDs
TRACKER_FILE = os.path.join(os.path.dirname(__file__), "processed_videos.json")


def load_processed_videos():
    """
    Load the list of already-processed video IDs from file.
    """
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r") as f:
            return json.load(f)
    return {"videos": {}}


def save_processed_videos(data):
    """
    Save the processed videos list to file.
    """
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)


def is_video_processed(video_id):
    """
    Check if a video has already been processed.
    """
    data = load_processed_videos()
    return video_id in data["videos"]


def mark_video_processed(video_id, title, channel):
    """
    Mark a video as processed so we don't send it again.
    """
    data = load_processed_videos()
    data["videos"][video_id] = {
        "title": title,
        "channel": channel,
        "processed_at": datetime.now().isoformat()
    }
    save_processed_videos(data)


def filter_new_videos(videos):
    """
    Filter out videos that have already been processed.
    Returns only new videos.
    """
    new_videos = []

    for video in videos:
        if is_video_processed(video["video_id"]):
            print(f"  ⏭ Skipping (already processed): {video['title'][:50]}...")
        else:
            new_videos.append(video)

    return new_videos


def mark_videos_processed(videos):
    """
    Mark multiple videos as processed after successfully sending newsletter.
    """
    for video in videos:
        mark_video_processed(video["video_id"], video["title"], video["channel"])


def get_processed_count():
    """
    Get the total number of videos we've processed.
    """
    data = load_processed_videos()
    return len(data["videos"])


# Utility to view/manage processed videos
if __name__ == "__main__":
    data = load_processed_videos()
    print(f"Total processed videos: {len(data['videos'])}\n")

    for video_id, info in data["videos"].items():
        print(f"• {info['channel']}: {info['title'][:50]}")
        print(f"  Processed: {info['processed_at']}\n")
