"""
SQLAlchemy database models for the interview platform.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum


Base = declarative_base()


def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4())


class SessionStatus(str, enum.Enum):
    """Session status enumeration."""
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class SpeakerType(str, enum.Enum):
    """Speaker type enumeration."""
    USER = "USER"
    AI = "AI"


class ProctoringEventType(str, enum.Enum):
    """Proctoring event type enumeration."""
    MULTIPLE_PERSONS = "MULTIPLE_PERSONS"
    NO_FACE = "NO_FACE"
    LOOKING_AWAY = "LOOKING_AWAY"
    TAB_SWITCH = "TAB_SWITCH"


class InterviewSession(Base):
    """Interview session model."""
    __tablename__ = "interview_sessions"
    
    session_id = Column(String, primary_key=True, default=generate_uuid)
    subject_name = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    livekit_room_id = Column(String, nullable=True)
    recording_url = Column(String, nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.SCHEDULED)
    resume_path = Column(String, nullable=True)
    reference_doc_path = Column(String, nullable=True)
    
    # Relationships
    transcripts = relationship("SessionTranscript", back_populates="session", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="session", cascade="all, delete-orphan")
    analytics = relationship("SessionAnalytics", back_populates="session", uselist=False, cascade="all, delete-orphan")
    proctoring_events = relationship("ProctoringEvent", back_populates="session", cascade="all, delete-orphan")


class Question(Base):
    """Question model."""
    __tablename__ = "questions"
    
    question_id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("interview_sessions.session_id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_order = Column(Integer, nullable=False)
    asked_at = Column(DateTime(timezone=True), server_default=func.now())
    user_answer = Column(Text, nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    response_time_seconds = Column(Float, nullable=True)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="questions")


class SessionTranscript(Base):
    """Session transcript model."""
    __tablename__ = "session_transcripts"
    
    transcript_id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("interview_sessions.session_id"), nullable=False)
    speaker = Column(Enum(SpeakerType), nullable=False)
    text_content = Column(Text, nullable=False)
    timestamp_offset_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("InterviewSession", back_populates="transcripts")


class SessionAnalytics(Base):
    """Session analytics model."""
    __tablename__ = "session_analytics"
    
    analytics_id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("interview_sessions.session_id"), nullable=False, unique=True)
    overall_score = Column(Float, nullable=True)
    fluency_score = Column(Float, nullable=True)
    accuracy_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    response_time_avg_seconds = Column(Float, nullable=True)
    questions_answered = Column(Integer, default=0)
    proctoring_flags_count = Column(Integer, default=0)
    topics_covered = Column(JSON, nullable=True)
    recommendations = Column(Text, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("InterviewSession", back_populates="analytics")


class ProctoringEvent(Base):
    """Proctoring event model."""
    __tablename__ = "proctoring_events"
    
    event_id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("interview_sessions.session_id"), nullable=False)
    event_type = Column(Enum(ProctoringEventType), nullable=False)
    timestamp_offset_ms = Column(Integer, nullable=False)
    confidence_score = Column(Float, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("InterviewSession", back_populates="proctoring_events")
