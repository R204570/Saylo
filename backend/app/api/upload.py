"""
File upload API endpoints.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from loguru import logger
import os
import shutil
from typing import Optional

from app.main import get_db
from app.config import settings
from app.services.document_service import document_service

router = APIRouter()


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Upload and process a resume.
    
    Args:
        file: Resume file (PDF, DOCX)
        session_id: Optional session ID to associate with
        db: Database session
        
    Returns:
        Upload result with file path and parsed data
    """
    try:
        # Validate file type
        allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF and DOCX are allowed."
            )
        
        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > settings.max_upload_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {settings.max_upload_size / 1024 / 1024}MB"
            )
        
        # Save file
        file_ext = os.path.splitext(file.filename)[1]
        file_path = os.path.join(settings.upload_dir, f"resume_{session_id or 'default'}{file_ext}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Resume uploaded: {file_path}")
        
        # Extract text
        file_type = "pdf" if file_ext == ".pdf" else "docx"
        text = document_service.extract_text(file_path, file_type)
        
        # Parse resume
        parsed_data = document_service.parse_resume(text)
        
        # Store in vector database for context retrieval
        collection_name = f"resume_{session_id or 'default'}"
        await document_service.process_and_store_document(
            file_path=file_path,
            file_type=file_type,
            collection_name=collection_name,
            metadata={
                "source": "resume",
                "session_id": session_id or "default",
                "filename": file.filename
            }
        )
        
        return {
            "success": True,
            "file_path": file_path,
            "parsed_data": parsed_data,
            "collection_name": collection_name
        }
        
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reference")
async def upload_reference_document(
    file: UploadFile = File(...),
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Upload and process a reference document.
    
    Args:
        file: Reference document (PDF, DOCX, TXT)
        session_id: Optional session ID to associate with
        db: Database session
        
    Returns:
        Upload result with file path and chunk count
    """
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain"
        ]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF, DOCX, and TXT are allowed."
            )
        
        # Validate file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > settings.max_upload_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {settings.max_upload_size / 1024 / 1024}MB"
            )
        
        # Save file
        file_ext = os.path.splitext(file.filename)[1]
        file_path = os.path.join(settings.upload_dir, f"reference_{session_id or 'default'}{file_ext}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Reference document uploaded: {file_path}")
        
        # Determine file type
        if file_ext == ".pdf":
            file_type = "pdf"
        elif file_ext in [".docx", ".doc"]:
            file_type = "docx"
        else:
            file_type = "txt"
        
        # Process and store in vector database
        collection_name = f"reference_{session_id or 'default'}"
        chunk_count = await document_service.process_and_store_document(
            file_path=file_path,
            file_type=file_type,
            collection_name=collection_name,
            metadata={
                "source": "reference",
                "session_id": session_id or "default",
                "filename": file.filename
            }
        )
        
        return {
            "success": True,
            "file_path": file_path,
            "chunk_count": chunk_count,
            "collection_name": collection_name
        }
        
    except Exception as e:
        logger.error(f"Error uploading reference document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
