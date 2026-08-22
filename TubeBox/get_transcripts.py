"""
Part 2: Extract Transcripts from YouTube Videos
This script uses the Supadata API to fetch transcripts reliably.
Unlike the youtube-transcript-api library, Supadata doesn't get blocked by YouTube.
"""

import os
import time
import requests
from dotenv import load_dotenv

# Load the API key from .env file
load_dotenv()
SUPADATA_API_KEY = os.getenv("SUPADATA_API_KEY")

# Supadata API endpoint for transcripts (works for YouTube, TikTok, Instagram, etc.)
SUPADATA_TRANSCRIPT_URL = "https://api.supadata.ai/v1/transcript"


def get_transcript(video_id):
    """
    Get the transcript for a YouTube video using Supadata API.

    How it works:
    - We send the video URL to Supadata's API
    - They fetch the transcript (they have infrastructure that doesn't get blocked)
    - We get back clean text with timestamps

    Returns the full text of everything said in the video, or None if unavailable.
    """
    # Check if API key is configured
    if not SUPADATA_API_KEY or SUPADATA_API_KEY == "your_supadata_api_key_here":
        print("  ⚠ SUPADATA_API_KEY not set in .env file")
        return None

    try:
        # Build the YouTube URL from the video ID
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"

        # Make the API request to Supadata
        # The 'text' format gives us just the plain text (no timestamps)
        response = requests.get(
            SUPADATA_TRANSCRIPT_URL,
            params={
                "url": youtube_url,
                "text": "true"  # Get plain text instead of timestamped segments
            },
            headers={
                "x-api-key": SUPADATA_API_KEY
            },
            timeout=60  # Transcripts can take a moment for long videos
        )

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()

            # The API returns content in the 'content' field when using text=true
            # Or 'transcript' field with segments when not using text=true
            if "content" in data and data["content"]:
                return data["content"].strip()
            elif "transcript" in data:
                # If we got segments, combine them into full text
                segments = data["transcript"]
                if segments:
                    full_text = " ".join(seg.get("text", "") for seg in segments)
                    return full_text.strip()

            print(f"  ⚠ No transcript content in response")
            return None

        elif response.status_code == 404:
            print(f"  ⚠ No transcript available for this video")
            return None
        elif response.status_code == 401:
            print(f"  ⚠ Invalid Supadata API key")
            return None
        elif response.status_code == 429:
            print(f"  ⚠ Rate limit exceeded - try again later")
            return None
        else:
            print(f"  ⚠ API error: {response.status_code} - {response.text[:200]}")
            return None

    except requests.exceptions.Timeout:
        print(f"  ⚠ Request timed out")
        return None
    except Exception as e:
        print(f"  ⚠ Error getting transcript: {e}")
        return None


def get_transcripts_for_videos(videos):
    """
    Get transcripts for a list of videos.
    Takes the video list from get_videos.py and adds transcripts.
    """
    print("\nExtracting transcripts via Supadata API...\n")
    print("=" * 60)

    for i, video in enumerate(videos):
        print(f"Getting transcript: {video['title'][:50]}...")

        transcript = get_transcript(video["video_id"])

        if transcript:
            video["transcript"] = transcript
            word_count = len(transcript.split())
            print(f"  ✓ Got {word_count} words\n")
        else:
            video["transcript"] = None
            print(f"  ✗ No transcript available\n")

        # Small delay between requests to be nice to the API
        if i < len(videos) - 1:
            time.sleep(1)

    # Filter out videos without transcripts
    videos_with_transcripts = [v for v in videos if v.get("transcript")]

    print("=" * 60)
    print(f"Got transcripts for {len(videos_with_transcripts)} of {len(videos)} videos")

    return videos_with_transcripts


# Test it standalone
if __name__ == "__main__":
    # Test with a sample video
    test_video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    print("Testing Supadata transcript extraction...")
    print(f"API Key configured: {'Yes' if SUPADATA_API_KEY and SUPADATA_API_KEY != 'your_supadata_api_key_here' else 'No'}")
    transcript = get_transcript(test_video_id)
    if transcript:
        print(f"Got transcript! First 200 chars:\n{transcript[:200]}...")
    else:
        print("Failed to get transcript")
