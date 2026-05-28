import os
import requests
from dotenv import load_dotenv
from normalizer import normalize_text
from db import upsert_live_video

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

BASE_URL = "https://www.googleapis.com/youtube/v3"

def get_uploads_playlist_id():
    """
    Fetches the uploads playlist ID for the configured YouTube channel.
    Supports channel ID (starts with UC) or handle (starts with @).
    Tries multiple resolution strategies for maximum compatibility.
    """
    if not API_KEY:
        raise Exception("YOUTUBE_API_KEY bulunamadı. Lütfen .env dosyasını kontrol edin.")
    if not CHANNEL_ID:
        raise Exception("YOUTUBE_CHANNEL_ID bulunamadı. Lütfen .env dosyasını kontrol edin.")

    url = f"{BASE_URL}/channels"
    clean_channel = CHANNEL_ID.strip()

    
    if clean_channel.startswith("UC"):
        params = {"part": "contentDetails", "id": clean_channel, "key": API_KEY}
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        items = response.json().get("items", [])
        if items:
            return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

   
    handle = clean_channel if clean_channel.startswith("@") else f"@{clean_channel}"
    params = {"part": "contentDetails", "forHandle": handle, "key": API_KEY}
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    items = response.json().get("items", [])
    if items:
        return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    
    handle_no_at = handle.lstrip("@")
    params = {"part": "contentDetails", "forHandle": handle_no_at, "key": API_KEY}
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    items = response.json().get("items", [])
    if items:
        return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    
    params = {"part": "contentDetails", "forUsername": handle_no_at, "key": API_KEY}
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    items = response.json().get("items", [])
    if items:
        return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    raise Exception(
        f"Kanal bulunamadı: '{CHANNEL_ID}'\n"
        f"Denenen yöntemler: forHandle='{handle}', forUsername='{handle_no_at}'\n"
        f"Çözüm: YouTube kanalının sayfasına gidin > Sayfa kaynağını görüntüleyin > "
        f"'channelId' arayın > UC ile başlayan ID'yi .env dosyasına yazın."
    )

def get_all_video_ids_from_uploads(uploads_playlist_id: str):
    """
    Fetches all video IDs from the uploads playlist.
    Implements pagination to retrieve the full history.
    """
    video_ids = []
    next_page_token = None

    while True:
        url = f"{BASE_URL}/playlistItems"
        params = {
            "part": "contentDetails",
            "playlistId": uploads_playlist_id,
            "maxResults": 50,
            "key": API_KEY
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()

        data = response.json()

        for item in data.get("items", []):
            video_id = item.get("contentDetails", {}).get("videoId")
            if video_id:
                video_ids.append(video_id)

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids

def chunk_list(items, chunk_size=50):
    """
    Yields successive chunk_size-sized chunks from items.
    """
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]

def get_video_details(video_ids: list[str]):
    """
    Fetches details for video IDs in batches of 50.
    """
    all_details = []

    for chunk in chunk_list(video_ids, 50):
        url = f"{BASE_URL}/videos"
        params = {
            "part": "snippet,contentDetails,liveStreamingDetails",
            "id": ",".join(chunk),
            "key": API_KEY
        }

        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()

        data = response.json()
        all_details.extend(data.get("items", []))

    return all_details

def is_completed_live_stream(video_item: dict) -> bool:
    """
    Determines if a video item is a completed live stream based on liveStreamingDetails.
    """
    live_details = video_item.get("liveStreamingDetails")
    if not live_details:
        return False

    return bool(
        live_details.get("actualStartTime")
        and live_details.get("actualEndTime")
    )

def extract_thumbnail(snippet: dict) -> str | None:
    """
    Extracts the highest resolution available thumbnail URL.
    """
    thumbnails = snippet.get("thumbnails", {})

    for size in ["maxres", "standard", "high", "medium", "default"]:
        if size in thumbnails:
            return thumbnails[size].get("url")

    return None

def sync_youtube_live_videos():
    """
    Runs the complete synchronization cycle:
    1. Resolves channel upload playlist
    2. Collects all upload video IDs
    3. Fetches details and filters for completed live streams
    4. Upserts completed live streams to PostgreSQL database
    """
    uploads_playlist_id = get_uploads_playlist_id()
    video_ids = get_all_video_ids_from_uploads(uploads_playlist_id)
    video_details = get_video_details(video_ids)

    saved_count = 0
    skipped_count = 0

    for item in video_details:
        if not is_completed_live_stream(item):
            skipped_count += 1
            continue

        snippet = item.get("snippet", {})
        live_details = item.get("liveStreamingDetails", {})

        youtube_video_id = item["id"]
        title = snippet.get("title", "")
        description = snippet.get("description", "")
        raw_text = f"{title}\n{description}"
        normalized_raw_text = normalize_text(raw_text)

        video = {
            "youtube_video_id": youtube_video_id,
            "title": title,
            "description": description,
            "raw_text": raw_text,
            "normalized_raw_text": normalized_raw_text,
            "video_url": f"https://www.youtube.com/watch?v={youtube_video_id}",
            "thumbnail_url": extract_thumbnail(snippet),
            "published_at": snippet.get("publishedAt"),
            "actual_start_time": live_details.get("actualStartTime"),
            "actual_end_time": live_details.get("actualEndTime")
        }

        upsert_live_video(video)
        saved_count += 1

    return {
        "total_video_count": len(video_ids),
        "live_saved_count": saved_count,
        "skipped_non_live_count": skipped_count
    }
