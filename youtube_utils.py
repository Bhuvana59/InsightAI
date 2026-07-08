import re


def extract_video_id(url: str):
    """
    Extracts the 11-character YouTube video ID from common URL formats.
    Returns the ID as a string, or None if the URL doesn't match any
    known YouTube pattern.
    """
    patterns = [
        r"(?:youtube\.com\/watch\?v=)([\w-]{11})",
        r"(?:youtu\.be\/)([\w-]{11})",
        r"(?:youtube\.com\/shorts\/)([\w-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None