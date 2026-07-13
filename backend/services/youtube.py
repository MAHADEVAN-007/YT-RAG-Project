import re

from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")


def get_transcript(video_id: str) -> list[dict]:
    transcript = YouTubeTranscriptApi().fetch(video_id)
    return [{"text": s.text, "start": s.start, "duration": s.duration} for s in transcript]


def format_full_text(segments: list[dict]) -> str:
    return " ".join(seg["text"] for seg in segments)
