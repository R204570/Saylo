"""
Interview interaction API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from loguru import logger

from app.main import get_db
from app.models import InterviewSession, Question, SessionTranscript, SpeakerType
from app.services.ollama_service import ollama_service
from app.services.vector_service import vector_service

router = APIRouter()


class GenerateQuestionRequest(BaseModel):
    """Request model for generating a question."""
    session_id: str
    question_number: int


class SubmitAnswerRequest(BaseModel):
    """Request model for submitting an answer."""
    session_id: str
    question_id: str
    answer_text: str


class AddTranscriptRequest(BaseModel):
    """Request model for adding transcript."""
    session_id: str
    speaker: str  # "USER" or "AI"
    text: str
    timestamp_offset_ms: int


@router.post("/generate-question")
async def generate_question(
    request: GenerateQuestionRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a new interview question.
    
    Args:
        request: Question generation request
        db: Database session
        
    Returns:
        Generated question
    """
    try:
        # Get session
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == request.session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get previous questions
        previous_questions = db.query(Question).filter(
            Question.session_id == request.session_id
        ).order_by(Question.question_order).all()
        
        previous_q_texts = [q.question_text for q in previous_questions]
        
        # Get resume context
        resume_collection = f"resume_{request.session_id}"
        resume_context = await vector_service.get_relevant_context(
            collection_name=resume_collection,
            query="candidate skills and experience",
            max_chunks=2
        )
        
        # Get reference context
        reference_collection = f"reference_{request.session_id}"
        reference_context = await vector_service.get_relevant_context(
            collection_name=reference_collection,
            query="interview topics and questions",
            max_chunks=3
        )
        
        # Generate question
        question_text = await ollama_service.generate_question(
            resume_context=resume_context,
            reference_context=reference_context,
            previous_questions=previous_q_texts,
            question_number=request.question_number,
            total_questions=8  # Default from settings
        )
        
        # Store question
        question = Question(
            session_id=request.session_id,
            question_text=question_text,
            question_order=request.question_number
        )
        
        db.add(question)
        db.commit()
        db.refresh(question)
        
        logger.info(f"Generated question {request.question_number} for session {request.session_id}")
        
        return {
            "question_id": question.question_id,
            "question_text": question.question_text,
            "question_order": question.question_order
        }
        
    except Exception as e:
        logger.error(f"Error generating question: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-answer")
async def submit_answer(
    request: SubmitAnswerRequest,
    db: Session = Depends(get_db)
):
    """
    Submit an answer to a question.
    
    Args:
        request: Answer submission request
        db: Database session
        
    Returns:
        Evaluation result
    """
    try:
        # Get question
        question = db.query(Question).filter(
            Question.question_id == request.question_id
        ).first()
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Update question with answer
        question.user_answer = request.answer_text
        question.answered_at = datetime.utcnow()
        
        if question.asked_at:
            response_time = (question.answered_at - question.asked_at).total_seconds()
            question.response_time_seconds = response_time
        
        # Get reference context for evaluation
        reference_collection = f"reference_{request.session_id}"
        reference_context = await vector_service.get_relevant_context(
            collection_name=reference_collection,
            query=question.question_text,
            max_chunks=3
        )
        
        # Evaluate answer
        evaluation = await ollama_service.evaluate_answer(
            question=question.question_text,
            answer=request.answer_text,
            reference_context=reference_context
        )
        
        db.commit()
        
        logger.info(f"Submitted answer for question {request.question_id}")
        
        return {
            "question_id": question.question_id,
            "evaluation": evaluation
        }
        
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-transcript")
async def add_transcript(
    request: AddTranscriptRequest,
    db: Session = Depends(get_db)
):
    """
    Add a transcript entry.
    
    Args:
        request: Transcript request
        db: Database session
        
    Returns:
        Created transcript
    """
    try:
        # Validate speaker
        speaker = SpeakerType.USER if request.speaker.upper() == "USER" else SpeakerType.AI
        
        # Create transcript
        transcript = SessionTranscript(
            session_id=request.session_id,
            speaker=speaker,
            text_content=request.text,
            timestamp_offset_ms=request.timestamp_offset_ms
        )
        
        db.add(transcript)
        db.commit()
        db.refresh(transcript)
        
        return {
            "transcript_id": transcript.transcript_id,
            "speaker": transcript.speaker,
            "text": transcript.text_content
        }
        
    except Exception as e:
        logger.error(f"Error adding transcript: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/transcript")
async def get_transcript(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get full transcript for a session.
    
    Args:
        session_id: Session ID
        db: Database session
        
    Returns:
        List of transcript entries
    """
    transcripts = db.query(SessionTranscript).filter(
        SessionTranscript.session_id == session_id
    ).order_by(SessionTranscript.timestamp_offset_ms).all()
    
    return [
        {
            "speaker": t.speaker,
            "text": t.text_content,
            "timestamp_ms": t.timestamp_offset_ms
        }
        for t in transcripts
    ]


@router.get("/{session_id}/questions")
async def get_questions(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all questions for a session.
    
    Args:
        session_id: Session ID
        db: Database session
        
    Returns:
        List of questions
    """
    questions = db.query(Question).filter(
        Question.session_id == session_id
    ).order_by(Question.question_order).all()
    
    return [
        {
            "question_id": q.question_id,
            "question_text": q.question_text,
            "question_order": q.question_order,
            "user_answer": q.user_answer,
            "response_time_seconds": q.response_time_seconds
        }
        for q in questions
    ]
