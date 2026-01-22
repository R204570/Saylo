"""
Speech-to-Text service using Faster Whisper.
Optimized for CPU to save GPU VRAM.
"""
from faster_whisper import WhisperModel
from typing import Optional, List, Tuple
from loguru import logger
from app.config import settings
import os


class STTService:
    """Speech-to-Text service using Whisper."""
    
    def __init__(self):
        self.model_size = settings.whisper_model
        self.device = settings.whisper_device
        self.model: Optional[WhisperModel] = None
        
    def load_model(self):
        """Load the Whisper model."""
        if self.model is None:
            try:
                logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
                
                # Use CPU to save GPU VRAM for LLM
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type="int8" if self.device == "cpu" else "float16"
                )
                
                logger.info("Whisper model loaded successfully")
                
            except Exception as e:
                logger.error(f"Error loading Whisper model: {e}")
                raise
    
    def transcribe_audio(
        self,
        audio_path: str,
        language: str = "en"
    ) -> Tuple[str, List[Dict]]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Language code (default: en)
            
        Returns:
            Tuple of (full_text, segments)
        """
        try:
            # Load model if not loaded
            if self.model is None:
                self.load_model()
            
            logger.info(f"Transcribing audio: {audio_path}")
            
            # Transcribe
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                vad_filter=True,  # Voice activity detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Collect segments
            full_text = ""
            segment_list = []
            
            for segment in segments:
                full_text += segment.text + " "
                segment_list.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                })
            
            logger.info(f"Transcription complete: {len(segment_list)} segments")
            
            return full_text.strip(), segment_list
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def transcribe_audio_chunk(
        self,
        audio_data: bytes,
        sample_rate: int = 16000
    ) -> str:
        """
        Transcribe audio chunk (for real-time processing).
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Sample rate of audio
            
        Returns:
            Transcribed text
        """
        try:
            # Load model if not loaded
            if self.model is None:
                self.load_model()
            
            # Save to temp file (Whisper needs file input)
            import tempfile
            import soundfile as sf
            import numpy as np
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
                
                # Convert bytes to numpy array
                audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Write to file
                sf.write(tmp_path, audio_array, sample_rate)
                
                # Transcribe
                text, _ = self.transcribe_audio(tmp_path)
                
                # Clean up
                os.unlink(tmp_path)
                
                return text
            
        except Exception as e:
            logger.error(f"Error transcribing audio chunk: {e}")
            raise
    
    def unload_model(self):
        """Unload the model to free memory."""
        if self.model is not None:
            del self.model
            self.model = None
            logger.info("Whisper model unloaded")


# Global instance
stt_service = STTService()
