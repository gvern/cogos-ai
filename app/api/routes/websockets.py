from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio
import base64
import io
import os
from datetime import datetime
from pathlib import Path

# Nécessaire pour traiter les données audio
try:
    import soundfile as sf
    import numpy as np
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False

# Pour la transcription
from ...core.voice_input import start_new_session

router = APIRouter(tags=["WebSockets"])

# Gestionnaire de connexions actives
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.audio_buffers: Dict[str, List[bytes]] = {}
        self.sessions: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.audio_buffers[client_id] = []
        self.sessions[client_id] = start_new_session()
        
        # Créer le répertoire pour les enregistrements si nécessaire
        session_id = self.sessions[client_id]
        voice_logs_dir = Path(f"logs/voice_sessions/{session_id}")
        voice_logs_dir.mkdir(exist_ok=True, parents=True)

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.audio_buffers:
            del self.audio_buffers[client_id]

    async def send_text(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

    def add_audio_chunk(self, client_id: str, audio_data: bytes):
        if client_id in self.audio_buffers:
            self.audio_buffers[client_id].append(audio_data)

    async def process_audio(self, client_id: str):
        """Traiter l'audio accumulé et le transcrire"""
        if client_id not in self.audio_buffers or not self.audio_buffers[client_id]:
            return None

        if not HAS_SOUNDFILE:
            await self.send_text(json.dumps({
                "type": "error",
                "data": "Dépendances audio manquantes (soundfile, numpy)"
            }), client_id)
            return None

        # Assembler tous les chunks audio
        audio_data = b''.join(self.audio_buffers[client_id])
        self.audio_buffers[client_id] = []  # Vider le buffer
        
        if not audio_data:
            return None
            
        try:
            # Convertir les données base64 en audio
            audio_bytes = base64.b64decode(audio_data)
            
            # Sauvegarder l'audio temporairement
            session_id = self.sessions[client_id]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            voice_file = Path(f"logs/voice_sessions/{session_id}/stream_{timestamp}.wav")
            
            with open(voice_file, "wb") as f:
                f.write(audio_bytes)
            
            # TODO: Appeler le service de transcription (comme Whisper)
            # Pour l'instant, simuler une transcription
            
            result = {
                "text": f"Simulation de transcription pour {voice_file.name}",
                "success": True,
                "audio_file": str(voice_file),
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            await self.send_text(json.dumps({
                "type": "error",
                "data": f"Erreur de traitement audio: {str(e)}"
            }), client_id)
            return None

# Créer le gestionnaire
manager = ConnectionManager()

@router.websocket("/ws/audio/{client_id}")
async def websocket_audio(websocket: WebSocket, client_id: str):
    """Point d'entrée WebSocket pour streaming audio"""
    await manager.connect(websocket, client_id)
    
    try:
        # Envoyer confirmation de connexion
        await manager.send_text(json.dumps({
            "type": "connection_established",
            "data": {
                "client_id": client_id,
                "session_id": manager.sessions[client_id]
            }
        }), client_id)
        
        while True:
            # Attendre des données du client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "audio_data":
                # Réception données audio
                audio_chunk = message["data"]
                manager.add_audio_chunk(client_id, audio_chunk)
                
            elif message["type"] == "process_audio":
                # Demande de traitement et transcription
                result = await manager.process_audio(client_id)
                if result:
                    await manager.send_text(json.dumps({
                        "type": "transcription",
                        "data": result
                    }), client_id)
                
            elif message["type"] == "ping":
                # Simple ping pour maintenir la connexion
                await manager.send_text(json.dumps({
                    "type": "pong",
                    "data": {"timestamp": datetime.now().isoformat()}
                }), client_id)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        await manager.send_text(json.dumps({
            "type": "error",
            "data": f"Erreur: {str(e)}"
        }), client_id)
        manager.disconnect(client_id) 