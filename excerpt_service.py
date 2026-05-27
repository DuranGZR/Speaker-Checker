import html
from normalizer import normalize_text

def highlight_name_in_text(raw_text: str, searched_name: str) -> str:
    """
    Returns the full raw_text as HTML with the matching name highlighted.
    Preserves original formatting and line breaks.
    """
    if not raw_text or not searched_name:
        return html.escape(raw_text or "")

    normalized_name = normalize_text(searched_name)
    lines = raw_text.splitlines()
    result_lines = []

    for line in lines:
        normalized_line = normalize_text(line)
        if normalized_name in normalized_line:
            # This line contains the match — highlight the whole line
            escaped = html.escape(line)
            result_lines.append(
                f'<span style="background:rgba(230,33,23,0.25);border-left:3px solid #e62117;padding:2px 6px;display:inline-block;width:100%;border-radius:3px;">{escaped}</span>'
            )
        else:
            result_lines.append(html.escape(line))

    return "<br>".join(result_lines)


def get_matched_excerpt(raw_text: str, searched_name: str, context_lines: int = 2) -> str:
    """
    Finds the line containing the searched name (in normalized form) and returns it
    along with surrounding context lines as a short summary.
    """
    if not raw_text:
        return ""

    lines = raw_text.splitlines()
    lines = [line.strip() for line in lines if line.strip()]

    normalized_name = normalize_text(searched_name)

    for index, line in enumerate(lines):
        normalized_line = normalize_text(line)

        if normalized_name in normalized_line:
            start = max(0, index - context_lines)
            end = min(len(lines), index + context_lines + 1)
            excerpt_lines = lines[start:end]

            formatted_lines = []
            for idx, eline in enumerate(excerpt_lines):
                orig_idx = start + idx
                if orig_idx == index:
                    formatted_lines.append(f"→ {eline}")
                else:
                    formatted_lines.append(f"  {eline}")

            return "\n".join(formatted_lines).strip()

    return raw_text[:500].strip() + ("..." if len(raw_text) > 500 else "")


def detect_match_type(excerpt: str, searched_name: str) -> str:
    """
    Detects if the match is a STRONG speaker pattern based on keywords,
    otherwise returns NORMAL_MENTION.
    """
    normalized_excerpt = normalize_text(excerpt)

    strong_keywords = [
        "konusmaci",
        "konusmacilar",
        "konuk",
        "konuklar",
        "konugumuz",
        "bizimle",
        "bizlerle",
        "ile birlikte",
        "moderator",
        "moderatoru",
        "sunumuyla",
        "sunan",
        "agirladi",
        "agirliyoruz"
    ]

    for keyword in strong_keywords:
        if keyword in normalized_excerpt:
            return "STRONG_SPEAKER_PATTERN"

    return "NORMAL_MENTION"
