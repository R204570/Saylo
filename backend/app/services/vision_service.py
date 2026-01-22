"""
Vision processing service for proctoring.
Uses LLaVA model for face detection and anomaly detection.
Optimized to run only when LLM is idle to save VRAM.
"""
import cv2
import numpy as np
from typing import Dict, Any, Optional
from loguru import logger
from app.config import settings
from app.services.ollama_service import ollama_service
import tempfile
import os
import asyncio


class VisionService:
    """Service for vision-based proctoring."""
    
    def __init__(self):
        self.enabled = settings.vision_enabled
        self.frame_interval = settings.vision_frame_interval
        self.last_frame_time = 0
        
    async def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyze a video frame for proctoring.
        
        Args:
            frame: Video frame as numpy array
            
        Returns:
            Analysis results with person count, face detection, etc.
        """
        if not self.enabled:
            return {
                "enabled": False,
                "message": "Vision processing disabled"
            }
        
        try:
            # Save frame to temporary file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                tmp_path = tmp_file.name
                cv2.imwrite(tmp_path, frame)
            
            # Prepare prompt for vision model
            prompt = """Analyze this image from an interview/exam setting. 
            
            Determine:
            1. Number of people visible
            2. Is a face clearly detected?
            3. Is the person looking at the camera?
            4. Any anomalies (multiple people, no face, looking away)?
            
            Return ONLY a JSON object with this exact structure:
            {
                "person_count": <number>,
                "face_detected": <true/false>,
                "looking_at_camera": <true/false>,
                "anomaly_detected": <true/false>,
                "anomaly_type": "<MULTIPLE_PERSONS|NO_FACE|LOOKING_AWAY|NONE>",
                "confidence_score": <0.0-1.0>
            }"""
            
            # Analyze with vision model
            response = await ollama_service.analyze_image(tmp_path, prompt)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            # Parse response
            import json
            
            # Extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            elif "{" in response:
                # Find JSON object in response
                start = response.index("{")
                end = response.rindex("}") + 1
                json_str = response[start:end]
            else:
                json_str = response.strip()
            
            result = json.loads(json_str)
            
            logger.info(f"Vision analysis: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing frame: {e}")
            return {
                "error": str(e),
                "person_count": 1,
                "face_detected": True,
                "looking_at_camera": True,
                "anomaly_detected": False,
                "anomaly_type": "NONE",
                "confidence_score": 0.0
            }
    
    def detect_face_opencv(self, frame: np.ndarray) -> bool:
        """
        Simple face detection using OpenCV (fallback).
        Faster but less accurate than LLaVA.
        
        Args:
            frame: Video frame
            
        Returns:
            True if face detected, False otherwise
        """
        try:
            # Load Haar Cascade for face detection
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            return len(faces) > 0
            
        except Exception as e:
            logger.error(f"Error in OpenCV face detection: {e}")
            return True  # Assume face present on error
    
    async def process_frame_simple(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Simple frame processing using OpenCV (no LLM).
        Use this for frequent checks to save VRAM.
        
        Args:
            frame: Video frame
            
        Returns:
            Simple analysis results
        """
        try:
            face_detected = self.detect_face_opencv(frame)
            
            return {
                "face_detected": face_detected,
                "anomaly_detected": not face_detected,
                "anomaly_type": "NO_FACE" if not face_detected else "NONE",
                "method": "opencv",
                "confidence_score": 0.8 if face_detected else 0.2
            }
            
        except Exception as e:
            logger.error(f"Error in simple frame processing: {e}")
            return {
                "face_detected": True,
                "anomaly_detected": False,
                "anomaly_type": "NONE",
                "method": "opencv",
                "confidence_score": 0.0,
                "error": str(e)
            }
    
    def should_process_frame(self, current_time: float) -> bool:
        """
        Determine if a frame should be processed based on interval.
        
        Args:
            current_time: Current timestamp
            
        Returns:
            True if frame should be processed
        """
        if current_time - self.last_frame_time >= self.frame_interval:
            self.last_frame_time = current_time
            return True
        return False
    
    async def process_video_stream(
        self,
        video_source: int = 0,
        duration_seconds: int = 60,
        callback = None
    ):
        """
        Process video stream for proctoring.
        
        Args:
            video_source: Video source (0 for webcam)
            duration_seconds: Duration to process
            callback: Optional callback function for results
        """
        if not self.enabled:
            logger.info("Vision processing disabled")
            return
        
        try:
            cap = cv2.VideoCapture(video_source)
            
            if not cap.isOpened():
                logger.error("Cannot open video source")
                return
            
            start_time = asyncio.get_event_loop().time()
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning("Cannot read frame")
                    break
                
                current_time = asyncio.get_event_loop().time()
                
                # Check if duration exceeded
                if current_time - start_time > duration_seconds:
                    break
                
                # Process frame at intervals
                if self.should_process_frame(current_time):
                    frame_count += 1
                    
                    # Use simple OpenCV detection for frequent checks
                    result = await self.process_frame_simple(frame)
                    
                    # Every 5th frame, use LLM for detailed analysis
                    if frame_count % 5 == 0:
                        result = await self.analyze_frame(frame)
                    
                    # Call callback if provided
                    if callback:
                        await callback(result)
                    
                    logger.info(f"Frame {frame_count}: {result}")
                
                # Small delay to avoid overwhelming CPU
                await asyncio.sleep(0.1)
            
            cap.release()
            logger.info(f"Processed {frame_count} frames")
            
        except Exception as e:
            logger.error(f"Error processing video stream: {e}")


# Global instance
vision_service = VisionService()
