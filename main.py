import os
import uuid
import shutil
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from faster_whisper import WhisperModel
from pydub import AudioSegment

# Configuration
UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {"wav", "mp3"}
MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes
MODEL_SIZE = "base"  # You can choose tiny, base, small, medium, large-v2, large-v3

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic models for response
class Segment(BaseModel):
    start: float
    end: float
    text: str

class TranscriptionResponse(BaseModel):
    text: str
    language: str
    segments: List[Segment]

# Singleton for Whisper model
class WhisperSingleton:
    _instance: Optional[WhisperModel] = None

    def __new__(cls) -> WhisperModel:
        if cls._instance is None:
            print(f"Loading Whisper model: {MODEL_SIZE}...")
            device = "cpu"
            compute_type = "int8"
            cls._instance = WhisperModel(MODEL_SIZE, device=device, compute_type=compute_type)
            print(f"Whisper model loaded on device: {device} with compute_type: {compute_type}")
        return cls._instance


# Initialize FastAPI app
app = FastAPI(
    title="Offline Audio/Video Transcription API",
    description="Transcribe audio and video files locally using Faster-Whisper.",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    # Load the model when the app starts
    WhisperSingleton()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint for service monitoring"""
    return {
        "status": "ok", 
        "model_loaded": WhisperSingleton._instance is not None,
        "model_size": MODEL_SIZE
    }

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/transcribe/", response_model=TranscriptionResponse)
async def transcribe_audio_video(file: UploadFile = File(...)):
    if file.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided for the uploaded file."
        )

    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types are: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Check file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)  # Reset file pointer to the beginning

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the maximum limit of {MAX_FILE_SIZE_MB} MB."
        )

    file_extension = file.filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    audio_file_path = None

    try:
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        transcription_source = file_path

        # Transcribe using Faster-Whisper
        model_instance = WhisperSingleton()
        segments, info = model_instance.transcribe(transcription_source, beam_size=5)

        full_text = ""
        transcribed_segments = []
        for segment in segments:
            full_text += segment.text
            transcribed_segments.append(
                Segment(start=segment.start, end=segment.end, text=segment.text)
            )

        return TranscriptionResponse(
            text=full_text,
            language=info.language,
            segments=transcribed_segments
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {e}"
        )
    finally:
        # Clean up uploaded and temporary audio files
        if os.path.exists(file_path):
            os.remove(file_path)
        if audio_file_path and os.path.exists(audio_file_path):
            os.remove(audio_file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1990)