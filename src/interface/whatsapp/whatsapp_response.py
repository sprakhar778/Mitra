import logging
import os
from io import BytesIO
from typing import Dict

import httpx
from fastapi import APIRouter, Request, Response
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from src.modules.image.image_to_text import ImageToText
from src.modules.speech.speech_to_text import SpeechToText

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level singletons (initialised once at startup)
# ---------------------------------------------------------------------------
speech_to_text = SpeechToText()
image_to_text = ImageToText()

# LLM — single shared instance, stateless call per request
llm = ChatOpenAI(model="gpt-4o", temperature=0.7, max_tokens=1000)

# ---------------------------------------------------------------------------
# WhatsApp credentials (set these in your .env)
# ---------------------------------------------------------------------------
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"

whatsapp_router = APIRouter()


# ---------------------------------------------------------------------------
# Main route — handles both webhook verification (GET) and messages (POST)
# ---------------------------------------------------------------------------
@whatsapp_router.api_route("/whatsapp_response", methods=["GET", "POST"])
async def whatsapp_handler(request: Request) -> Response:
    """Entry point for all WhatsApp Cloud API events."""

    # --- Webhook verification handshake ---
    if request.method == "GET":
        return _verify_webhook(request)

    # --- Incoming event ---
    try:
        data = await request.json()
        change_value = data["entry"][0]["changes"][0]["value"]

        if "messages" in change_value:
            return await _handle_message(change_value["messages"][0])

        if "statuses" in change_value:
            # Delivery / read receipts — nothing to do
            return Response(content="Status update received", status_code=200)

        return Response(content="Unknown event type", status_code=400)

    except Exception:
        logger.exception("Unhandled error in whatsapp_handler")
        return Response(content="Internal server error", status_code=500)


# ---------------------------------------------------------------------------
# Webhook verification
# ---------------------------------------------------------------------------
def _verify_webhook(request: Request) -> Response:
    """Respond to Meta's hub challenge during webhook registration."""
    params = request.query_params
    if params.get("hub.verify_token") == WHATSAPP_VERIFY_TOKEN:
        return Response(content=params.get("hub.challenge"), status_code=200)
    return Response(content="Verification token mismatch", status_code=403)


# ---------------------------------------------------------------------------
# Message handling
# ---------------------------------------------------------------------------
async def _handle_message(message: Dict) -> Response:
    """Parse an incoming message, call the LLM, and reply."""
    from_number = message["from"]
    msg_type = message["type"]

    # Build the text content we'll send to the LLM
    content = await _extract_content(message, msg_type)

    # Call the LLM directly — no graph, no agent overhead
    reply = await _call_llm(content)

    # Send the reply back to the user
    success = await send_text_message(from_number, reply)
    if not success:
        return Response(content="Failed to send message", status_code=500)

    return Response(content="Message processed", status_code=200)


async def _extract_content(message: Dict, msg_type: str) -> str:
    """Turn any supported message type into a plain-text string for the LLM."""

    if msg_type == "text":
        return message["text"]["body"]

    if msg_type == "audio":
        return await _transcribe_audio(message["audio"]["id"])

    if msg_type == "image":
        caption = message.get("image", {}).get("caption", "")
        image_bytes = await _download_media(message["image"]["id"])
        description = await image_to_text.analyze_image(
            image_bytes,
            "Describe what you see in this image in the context of our conversation.",
        )
        # Combine caption (if any) with the vision model's description
        return f"{caption}\n[Image: {description}]".strip()

    # Unsupported type — let the LLM handle it gracefully
    return f"[Unsupported message type: {msg_type}]"


async def _call_llm(content: str) -> str:
    """Send content to the LLM and return its text reply."""
    response = await llm.ainvoke([HumanMessage(content=content)])
    return response.content


# ---------------------------------------------------------------------------
# Media helpers
# ---------------------------------------------------------------------------
async def _download_media(media_id: str) -> bytes:
    """Fetch raw bytes for any WhatsApp media item by its ID."""
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

    async with httpx.AsyncClient() as client:
        # Step 1: resolve the media ID to a download URL
        meta = await client.get(f"{GRAPH_API_BASE}/{media_id}", headers=headers)
        meta.raise_for_status()
        download_url = meta.json()["url"]

        # Step 2: download the actual file
        media = await client.get(download_url, headers=headers)
        media.raise_for_status()
        return media.content


async def _transcribe_audio(audio_id: str) -> str:
    """Download a WhatsApp audio message and return its transcript."""
    audio_bytes = await _download_media(audio_id)
    return await speech_to_text.transcribe(audio_bytes)


# ---------------------------------------------------------------------------
# Sending messages
# ---------------------------------------------------------------------------
async def send_text_message(to: str, body: str) -> bool:
    """Send a plain-text WhatsApp message. Returns True on success."""
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    return await _post_to_whatsapp("messages", payload)


async def _post_to_whatsapp(endpoint: str, payload: Dict) -> bool:
    """POST JSON to the WhatsApp Graph API. Returns True if HTTP 200."""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    url = f"{GRAPH_API_BASE}/{WHATSAPP_PHONE_NUMBER_ID}/{endpoint}"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        logger.error("WhatsApp API error %s: %s", response.status_code, response.text)

    return response.status_code == 200