"""
Session management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from loguru import logger

from app.main import get_db
from app.models import InterviewSession, SessionStatus, SessionAnalytics

router = APIRouter()


class CreateSessionRequest(BaseModel):
    """Request model for creating a session."""
    subject_name: str
    resume_path: Optional[str] = None
    reference_doc_path: Optional[str] = None


class SessionResponse(BaseModel):
    """Response model for session."""
    session_id: str
    subject_name: str
    started_at: datetime
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]
    status: str
    livekit_room_id: Optional[str]
    
    class Config:
        from_attributes = True


@router.post("/create", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new interview session.
    
    Args:
        request: Session creation request
        db: Database session
        
    Returns:
        Created session
    """
    try:
        # Create session
        session = InterviewSession(
            subject_name=request.subject_name,
            resume_path=request.resume_path,
            reference_doc_path=request.reference_doc_path,
            status=SessionStatus.SCHEDULED
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"Created session: {session.session_id}")
        
        return session
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get session by ID.
    
    Args:
        session_id: Session ID
        db: Database session
        
    Returns:
        Session details
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List all sessions.
    
    Args:
        limit: Maximum number of sessions to return
        offset: Offset for pagination
        db: Database session
        
    Returns:
        List of sessions
    """
    sessions = db.query(InterviewSession).order_by(
        InterviewSession.started_at.desc()
    ).limit(limit).offset(offset).all()
    
    return sessions


@router.post("/{session_id}/start")
async def start_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Start an interview session.
    
    Args:
        session_id: Session ID
        db: Database session
        
    Returns:
        Updated session with LiveKit room details
    """
    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update session status
        session.status = SessionStatus.IN_PROGRESS
        session.started_at = datetime.utcnow()
        
        # Create LiveKit room (will implement in livekit_service)
        # For now, use session_id as room name
        session.livekit_room_id = f"room_{session_id}"
        
        db.commit()
        db.refresh(session)
        
        logger.info(f"Started session: {session_id}")
        
        return {
            "session_id": session.session_id,
            "livekit_room_id": session.livekit_room_id,
            "status": session.status
        }
        
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/end")
async def end_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    End an interview session.
    
    Args:
        session_id: Session ID
        db: Database session
        
    Returns:
        Updated session
    """
    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update session
        session.status = SessionStatus.COMPLETED
        session.ended_at = datetime.utcnow()
        
        if session.started_at:
            duration = (session.ended_at - session.started_at).total_seconds()
            session.duration_seconds = int(duration)
        
        db.commit()
        db.refresh(session)
        
        logger.info(f"Ended session: {session_id}")
        
        return {
            "session_id": session.session_id,
            "status": session.status,
            "duration_seconds": session.duration_seconds
        }
        
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/analytics")
async def get_session_analytics(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get analytics for a session.
    
    Args:
        session_id: Session ID
        db: Database session
        
    Returns:
        Session analytics
    """
    analytics = db.query(SessionAnalytics).filter(
        SessionAnalytics.session_id == session_id
    ).first()
    
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    
    return {
        "session_id": analytics.session_id,
        "overall_score": analytics.overall_score,
        "fluency_score": analytics.fluency_score,
        "accuracy_score": analytics.accuracy_score,
        "confidence_score": analytics.confidence_score,
        "response_time_avg_seconds": analytics.response_time_avg_seconds,
        "questions_answered": analytics.questions_answered,
        "proctoring_flags_count": analytics.proctoring_flags_count,
        "topics_covered": analytics.topics_covered,
        "recommendations": analytics.recommendations
    }
