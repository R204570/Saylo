"""
Document processing service for PDF and DOCX files.
Handles text extraction, chunking, and vectorization.
"""
import pypdf
import pdfplumber
from docx import Document
from typing import List, Dict, Any, Tuple
from loguru import logger
from app.config import settings
from app.services.vector_service import vector_service
import re


class DocumentService:
    """Service for processing and vectorizing documents."""
    
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        try:
            text = ""
            
            # Try with pdfplumber first (better for complex PDFs)
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
            except Exception as e:
                logger.warning(f"pdfplumber failed, trying pypdf: {e}")
                
                # Fallback to pypdf
                with open(file_path, "rb") as f:
                    pdf_reader = pypdf.PdfReader(f)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """
        Extract text from a DOCX file.
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Extracted text
        """
        try:
            doc = Document(file_path)
            text = "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """
        Extract text from a document.
        
        Args:
            file_path: Path to the file
            file_type: File type (pdf, docx, txt)
            
        Returns:
            Extracted text
        """
        file_type = file_type.lower()
        
        if file_type == "pdf":
            return self.extract_text_from_pdf(file_path)
        elif file_type in ["docx", "doc"]:
            return self.extract_text_from_docx(file_path)
        elif file_type == "txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', '', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        # Simple word-based chunking
        words = text.split()
        chunks = []
        
        i = 0
        while i < len(words):
            # Get chunk
            chunk_words = words[i:i + self.chunk_size]
            chunk = " ".join(chunk_words)
            chunks.append(chunk)
            
            # Move forward with overlap
            i += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    async def process_and_store_document(
        self,
        file_path: str,
        file_type: str,
        collection_name: str,
        metadata: Dict[str, Any] = None
    ) -> int:
        """
        Process a document and store in vector database.
        
        Args:
            file_path: Path to the document
            file_type: Type of file (pdf, docx, txt)
            collection_name: ChromaDB collection name
            metadata: Additional metadata
            
        Returns:
            Number of chunks created
        """
        try:
            # Extract text
            logger.info(f"Extracting text from {file_path}")
            text = self.extract_text(file_path, file_type)
            
            # Clean text
            text = self.clean_text(text)
            
            # Chunk text
            logger.info(f"Chunking text (chunk_size={self.chunk_size}, overlap={self.chunk_overlap})")
            chunks = self.chunk_text(text)
            
            # Prepare metadata
            base_metadata = metadata or {}
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    **base_metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                metadatas.append(chunk_metadata)
                ids.append(f"{collection_name}_chunk_{i}")
            
            # Store in vector database
            logger.info(f"Storing {len(chunks)} chunks in collection '{collection_name}'")
            await vector_service.add_documents(
                collection_name=collection_name,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully processed document: {len(chunks)} chunks created")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise
    
    def parse_resume(self, text: str) -> Dict[str, Any]:
        """
        Parse resume text to extract key information.
        
        Args:
            text: Resume text
            
        Returns:
            Parsed resume data
        """
        # Simple keyword-based parsing
        # In production, use a proper resume parser or NLP model
        
        parsed = {
            "skills": [],
            "experience": [],
            "education": [],
            "summary": ""
        }
        
        # Extract skills (simple keyword matching)
        skill_keywords = [
            "python", "java", "javascript", "react", "node", "sql", "aws",
            "docker", "kubernetes", "machine learning", "ai", "data science"
        ]
        
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                parsed["skills"].append(skill.title())
        
        # Extract sections (very basic)
        lines = text.split("\n")
        current_section = None
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if any(word in line_lower for word in ["experience", "work history"]):
                current_section = "experience"
            elif any(word in line_lower for word in ["education", "academic"]):
                current_section = "education"
            elif any(word in line_lower for word in ["summary", "objective"]):
                current_section = "summary"
            elif current_section and line.strip():
                if current_section == "summary":
                    parsed["summary"] += line + " "
                elif current_section in ["experience", "education"]:
                    parsed[current_section].append(line.strip())
        
        parsed["summary"] = parsed["summary"].strip()
        
        return parsed


# Global instance
document_service = DocumentService()
