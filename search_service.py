from normalizer import normalize_text
from db import search_videos_by_name
from excerpt_service import get_matched_excerpt, detect_match_type, highlight_name_in_text

def search_name_in_live_videos(name: str):
    """
    Normalizes the search query, queries the database, extracts contextual matching excerpts,
    and returns a structured response mapping to the UI search results.
    """
    normalized_name = normalize_text(name)

    if not normalized_name:
        return {
            "searched_name": name,
            "result_count": 0,
            "results": []
        }

    rows = search_videos_by_name(normalized_name)
    results = []

    for row in rows:
        raw_text = row.get("raw_text") or ""
        excerpt = get_matched_excerpt(raw_text, name)
        match_type = detect_match_type(excerpt, name)
        highlighted_desc = highlight_name_in_text(row.get("description") or "", name)

        results.append({
            "id": row["id"],
            "youtube_video_id": row["youtube_video_id"],
            "title": row["title"],
            "description": row.get("description") or "",
            "highlighted_description": highlighted_desc,
            "raw_text": raw_text,
            "video_url": row["video_url"],
            "thumbnail_url": row["thumbnail_url"],
            "published_at": row["published_at"],
            "actual_start_time": row["actual_start_time"],
            "actual_end_time": row["actual_end_time"],
            "matched_excerpt": excerpt,
            "match_type": match_type
        })

    return {
        "searched_name": name,
        "normalized_name": normalized_name,
        "result_count": len(results),
        "results": results
    }
