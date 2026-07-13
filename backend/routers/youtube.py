from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from Models.models import User
from Schema.schema import YTTranscriptRequest, YTTranscriptResponse, TranscriptSegment
from backend.auth import get_current_user
from backend.services.youtube import extract_video_id, get_transcript, format_full_text

router = APIRouter(prefix="/api/youtube", tags=["youtube"])


@router.post("/transcript", response_model=YTTranscriptResponse)
async def fetch_transcript(
    body: YTTranscriptRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        video_id = extract_video_id(body.url)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        segments = get_transcript(video_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail=f"Failed to fetch transcript: {str(e)}")

    full_text = format_full_text(segments)

    return YTTranscriptResponse(
        video_id=video_id,
        title=f"YouTube Video ({video_id})",
        segments=[TranscriptSegment(**s) for s in segments],
        full_text=full_text,
    )
