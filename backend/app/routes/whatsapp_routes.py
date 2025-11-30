"""
WhatsApp Webhook Routes
Handles incoming WhatsApp messages from Twilio.
"""

from fastapi import APIRouter, Request, Form, HTTPException, BackgroundTasks
from typing import Optional
import logging
import requests
import tempfile
import os

from app.services.whatsapp_service import get_whatsapp_service
from app.services.rag_pipeline import get_rag_pipeline

router = APIRouter(prefix="/api/v1/whatsapp", tags=["whatsapp"])
logger = logging.getLogger(__name__)

async def process_whatsapp_message(
    from_number: str, 
    message_body: str,
    media_url: Optional[str] = None,
    media_type: Optional[str] = None
):
    """
    Process incoming message in background and send response.
    """
    try:
        # 1. Get RAG Pipeline
        pipeline = get_rag_pipeline()
        
        query_text = message_body
        
        # 2. Handle Audio
        if media_url and media_type and media_type.startswith("audio/"):
            try:
                # Download audio to temp file
                logger.info(f"🎤 Downloading audio from {media_url}")
                
                # Note: Twilio Media URLs often require Basic Auth if "Enforce HTTP Basic Auth on Media URLs" is enabled.
                # For this demo, we'll try a simple GET. If it fails (401/403), we'd need to add auth.
                # In a real app, use: requests.get(media_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
                
                response = requests.get(media_url)
                
                if response.status_code == 200:
                    # Create temp file
                    # We use .ogg because WhatsApp voice notes are often OGG/Opus
                    suffix = ".ogg" 
                    if "mp3" in media_type: suffix = ".mp3"
                    elif "wav" in media_type: suffix = ".wav"
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
                        temp_audio.write(response.content)
                        temp_audio_path = temp_audio.name
                    
                    # Transcribe
                    logger.info(f"🎤 Transcribing audio file: {temp_audio_path}")
                    transcription = pipeline.transcribe_audio(temp_audio_path)
                    logger.info(f"📝 Transcription: {transcription}")
                    
                    # Clean up
                    try:
                        os.unlink(temp_audio_path)
                    except:
                        pass
                    
                    if transcription:
                        query_text = transcription
                        # Notify user we heard them
                        whatsapp = get_whatsapp_service()
                        whatsapp.send_message(to_number=from_number, body=f"🎤 *I heard:* \"{transcription}\"\n\nThinking...")
                else:
                    logger.error(f"Failed to download media: {response.status_code}")
            except Exception as e:
                logger.error(f"Error handling audio: {e}")

        # If we have no text (and audio failed or wasn't present), stop
        if not query_text:
            return

        # 3. Generate Answer (using RAG)
        # Simple session ID from phone number
        session_id = f"wa_{from_number.replace('whatsapp:', '').replace('+', '')}"
        
        result = pipeline.answer_query(
            query=query_text,
            use_graph=True,
            use_vector=True
        )
        
        answer = result.get("answer", "Sorry, I couldn't generate a response.")
        
        # 4. Format Response for WhatsApp
        # WhatsApp supports basic formatting: *bold*, _italic_, ~strikethrough~, ```monospace```
        formatted_answer = answer
        
        # Add sources if available
        sources = result.get("sources", [])
        if sources:
            formatted_answer += "\n\n*Sources:*"
            for src in sources[:3]:
                title = src.get("title", "Document")
                section = src.get("section", "")
                if section:
                    formatted_answer += f"\n- {title} ({section})"
                else:
                    formatted_answer += f"\n- {title}"
        
        # 5. Send Response via WhatsApp Service
        whatsapp = get_whatsapp_service()
        whatsapp.send_message(to_number=from_number, body=formatted_answer)
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {e}")
        # Try to send error message
        try:
            whatsapp = get_whatsapp_service()
            whatsapp.send_message(to_number=from_number, body="Sorry, I encountered an error processing your request.")
        except:
            pass

@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    From: str = Form(...),
    Body: str = Form(None),
    NumMedia: int = Form(0),
    MediaUrl0: str = Form(None),
    MediaContentType0: str = Form(None)
):
    """
    Twilio Webhook Endpoint.
    Receives incoming WhatsApp messages.
    """
    logger.info(f"📩 WhatsApp received from {From}. Body: {Body}, Media: {NumMedia}")
    
    # Offload processing to background task to respond quickly to Twilio
    background_tasks.add_task(
        process_whatsapp_message, 
        From, 
        Body or "",
        MediaUrl0,
        MediaContentType0
    )
    
    return {"status": "received"}
