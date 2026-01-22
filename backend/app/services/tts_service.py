"""
Text-to-Speech service using Piper TTS.
Optimized for CPU to save GPU VRAM.
"""
import subprocess
import os
import tempfile
from typing import Optional
from loguru import logger
from app.config import settings


class TTSService:
    """Text-to-Speech service using Piper."""
    
    def __init__(self):
        self.voice = settings.piper_voice
        self.model_path: Optional[str] = None
        self.config_path: Optional[str] = None
        
    def download_voice_model(self):
        """Download Piper voice model if not exists."""
        try:
            # Piper models are typically stored in a models directory
            models_dir = os.path.join(os.path.dirname(__file__), "../../models/piper")
            os.makedirs(models_dir, exist_ok=True)
            
            # Model files
            model_file = f"{self.voice}.onnx"
            config_file = f"{self.voice}.onnx.json"
            
            self.model_path = os.path.join(models_dir, model_file)
            self.config_path = os.path.join(models_dir, config_file)
            
            # Check if model exists
            if os.path.exists(self.model_path) and os.path.exists(self.config_path):
                logger.info(f"Piper voice model already exists: {self.voice}")
                return
            
            # Download model
            logger.info(f"Downloading Piper voice model: {self.voice}")
            
            # Download URLs (from Piper releases)
            base_url = "https://github.com/rhasspy/piper/releases/download/v1.2.0"
            model_url = f"{base_url}/{model_file}"
            config_url = f"{base_url}/{config_file}"
            
            # Download using curl or wget
            import urllib.request
            
            urllib.request.urlretrieve(model_url, self.model_path)
            urllib.request.urlretrieve(config_url, self.config_path)
            
            logger.info("Piper voice model downloaded successfully")
            
        except Exception as e:
            logger.warning(f"Error downloading Piper model: {e}")
            logger.info("Will attempt to use system Piper installation")
    
    def synthesize_speech(
        self,
        text: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            output_path: Optional output file path (if None, creates temp file)
            
        Returns:
            Path to generated audio file
        """
        try:
            # Create output path if not provided
            if output_path is None:
                tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                output_path = tmp_file.name
                tmp_file.close()
            
            # Prepare Piper command
            # Try using piper binary if available
            try:
                # Check if piper is installed
                subprocess.run(["piper", "--version"], capture_output=True, check=True)
                
                # Use piper CLI
                cmd = [
                    "piper",
                    "--model", self.model_path or self.voice,
                    "--output_file", output_path
                ]
                
                # Run piper
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate(input=text)
                
                if process.returncode != 0:
                    raise Exception(f"Piper failed: {stderr}")
                
                logger.info(f"Speech synthesized: {output_path}")
                return output_path
                
            except FileNotFoundError:
                # Piper not installed, use alternative
                logger.warning("Piper not found, using fallback TTS")
                return self._fallback_tts(text, output_path)
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            raise
    
    def _fallback_tts(self, text: str, output_path: str) -> str:
        """
        Fallback TTS using gTTS (Google TTS) or pyttsx3.
        
        Args:
            text: Text to synthesize
            output_path: Output file path
            
        Returns:
            Path to generated audio file
        """
        try:
            # Try gTTS first (requires internet)
            try:
                from gtts import gTTS
                
                tts = gTTS(text=text, lang='en', slow=False)
                tts.save(output_path)
                
                logger.info(f"Speech synthesized using gTTS: {output_path}")
                return output_path
                
            except ImportError:
                logger.warning("gTTS not available")
            
            # Try pyttsx3 (offline, but quality varies)
            try:
                import pyttsx3
                
                engine = pyttsx3.init()
                engine.save_to_file(text, output_path)
                engine.runAndWait()
                
                logger.info(f"Speech synthesized using pyttsx3: {output_path}")
                return output_path
                
            except ImportError:
                logger.error("No TTS engine available")
                raise Exception("No TTS engine available. Please install piper, gTTS, or pyttsx3")
            
        except Exception as e:
            logger.error(f"Error in fallback TTS: {e}")
            raise
    
    async def synthesize_speech_async(
        self,
        text: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Async wrapper for speech synthesis.
        
        Args:
            text: Text to synthesize
            output_path: Optional output file path
            
        Returns:
            Path to generated audio file
        """
        import asyncio
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.synthesize_speech,
            text,
            output_path
        )


# Global instance
tts_service = TTSService()
