from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
import tempfile
import os
from typing import Optional
import shutil
from datetime import datetime
from pathlib import Path

from ..schemas.base import AudioTranscriptResponse, ApiResponse
from ...core.voice_input import (
    listen_from_microphone, 
    start_new_session,
    get_session_history
)

router = APIRouter(prefix="/voice", tags=["Voice"])


@router.post("/session", response_model=ApiResponse)
async def create_session():
    """Démarre une nouvelle session d'enregistrement vocal"""
    try:
        session_id = start_new_session()
        return ApiResponse(data={"session_id": session_id})
    except Exception as e:
        return ApiResponse(status="error", message=str(e))


@router.get("/sessions/{session_id}/history", response_model=ApiResponse)
async def session_history(session_id: str):
    """Récupère l'historique des enregistrements d'une session"""
    try:
        history = get_session_history(session_id)
        return ApiResponse(data={"history": history})
    except Exception as e:
        return ApiResponse(status="error", message=str(e))


@router.post("/upload", response_model=ApiResponse)
async def upload_audio(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None)
):
    """Upload et transcription d'un fichier audio"""
    if not session_id:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Créer le dossier temporaire pour les enregistrements
    voice_logs_dir = Path("logs/voice_sessions") / session_id
    voice_logs_dir.mkdir(exist_ok=True, parents=True)
    
    # Sauvegarder le fichier
    timestamp = datetime.now().isoformat()
    audio_file = voice_logs_dir / f"upload_{timestamp.replace(':', '-')}.wav"
    
    try:
        # Sauvegarder le fichier audio uploadé
        with open(audio_file, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        # TODO: Transcrire l'audio en utilisant un service comme Whisper
        # Pour l'instant, nous simulons une transcription réussie
        text = "Transcription simulée pour ce fichier audio"
        
        response = AudioTranscriptResponse(
            text=text,
            success=True,
            audio_file=str(audio_file),
            timestamp=timestamp
        )
        
        return ApiResponse(data=response.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()


@router.get("/download/{session_id}/{filename}")
async def download_audio(session_id: str, filename: str):
    """Télécharge un fichier audio d'une session"""
    file_path = Path("logs/voice_sessions") / session_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier audio non trouvé")
    
    return FileResponse(path=str(file_path), filename=filename, media_type="audio/wav")


# Note: Dans une application réelle, l'enregistrement direct depuis le 
# microphone serait géré par le frontend et envoyé au backend via WebSockets
# ou en uploadant le fichier audio. Cette route simule ce comportement. 