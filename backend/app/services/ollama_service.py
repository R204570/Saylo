"""
Ollama service for LLM interactions.
Handles question generation, answer evaluation, and context-aware responses.
"""
import httpx
import json
from typing import List, Dict, Any, Optional
from loguru import logger
from app.config import settings


class OllamaService:
    """Service for interacting with Ollama LLM."""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.llm_model = settings.ollama_llm_model
        self.embedding_model = settings.ollama_embedding_model
        self.vision_model = settings.ollama_vision_model
        self.max_tokens = settings.max_context_tokens
        
    async def generate_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a completion from the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": self.llm_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens or self.max_tokens
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "").strip()
                
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise
    
    async def generate_question(
        self, 
        resume_context: str, 
        reference_context: str,
        previous_questions: List[str],
        question_number: int,
        total_questions: int
    ) -> str:
        """
        Generate an interview question based on context.
        
        Args:
            resume_context: Relevant resume information
            reference_context: Retrieved reference material
            previous_questions: List of already asked questions
            question_number: Current question number
            total_questions: Total questions to ask
            
        Returns:
            Generated question text
        """
        system_prompt = """You are an expert technical interviewer. Generate thoughtful, relevant interview questions based on the candidate's resume and reference materials. 

Guidelines:
- Ask questions that assess both theoretical knowledge and practical experience
- Build upon previous questions naturally
- Vary difficulty appropriately
- Be specific and clear
- Focus on topics mentioned in the resume or reference materials"""

        previous_q_text = "\n".join([f"- {q}" for q in previous_questions]) if previous_questions else "None"
        
        prompt = f"""Generate interview question {question_number} of {total_questions}.

CANDIDATE RESUME:
{resume_context}

REFERENCE MATERIALS:
{reference_context}

PREVIOUS QUESTIONS:
{previous_q_text}

Generate a single, clear interview question that:
1. Is relevant to the candidate's background
2. Assesses important skills for the role
3. Doesn't repeat previous questions
4. Can be answered in 1-3 minutes

Return ONLY the question text, nothing else."""

        question = await self.generate_completion(prompt, system_prompt, temperature=0.8)
        return question
    
    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        reference_context: str
    ) -> Dict[str, Any]:
        """
        Evaluate a user's answer to a question.
        
        Args:
            question: The question that was asked
            answer: The user's answer
            reference_context: Relevant reference material
            
        Returns:
            Evaluation results with scores and feedback
        """
        system_prompt = """You are an expert interviewer evaluating candidate responses. Provide fair, constructive feedback.

Evaluate answers on:
- Correctness: Technical accuracy
- Completeness: Coverage of key points
- Clarity: Communication effectiveness
- Depth: Understanding demonstrated

Return your evaluation as JSON with this exact structure:
{
    "correctness_score": 0-10,
    "completeness_score": 0-10,
    "clarity_score": 0-10,
    "overall_score": 0-10,
    "feedback": "Constructive feedback here",
    "strengths": ["strength 1", "strength 2"],
    "improvements": ["area 1", "area 2"]
}"""

        prompt = f"""Evaluate this interview response:

QUESTION:
{question}

CANDIDATE'S ANSWER:
{answer}

REFERENCE CONTEXT:
{reference_context}

Provide a thorough evaluation in JSON format."""

        response = await self.generate_completion(prompt, system_prompt, temperature=0.3)
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            evaluation = json.loads(json_str)
            return evaluation
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse evaluation JSON: {e}")
            # Return default evaluation
            return {
                "correctness_score": 5,
                "completeness_score": 5,
                "clarity_score": 5,
                "overall_score": 5,
                "feedback": "Unable to evaluate answer properly.",
                "strengths": [],
                "improvements": []
            }
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            url = f"{self.base_url}/api/embeddings"
            
            embeddings = []
            for text in texts:
                payload = {
                    "model": self.embedding_model,
                    "prompt": text
                }
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    result = response.json()
                    embeddings.append(result.get("embedding", []))
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    async def analyze_image(self, image_path: str, prompt: str) -> str:
        """
        Analyze an image using vision model.
        
        Args:
            image_path: Path to the image file
            prompt: Analysis prompt
            
        Returns:
            Analysis result
        """
        try:
            url = f"{self.base_url}/api/generate"
            
            # Read and encode image
            import base64
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            payload = {
                "model": self.vision_model,
                "prompt": prompt,
                "images": [image_data],
                "stream": False
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "").strip()
                
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            raise
    
    async def check_health(self) -> bool:
        """
        Check if Ollama service is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False


# Global instance
ollama_service = OllamaService()
