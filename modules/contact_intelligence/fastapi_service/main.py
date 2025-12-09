import os
import json
import base64
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Request
from pydantic import BaseModel
from supabase import create_client, Client
from openai import AsyncOpenAI
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# --- CONFIGURATION ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ENCRYPTION_KEY = os.getenv("CONTACT_ENCRYPTION_KEY") # Must be 32 bytes base64 encoded

# --- INITIALIZATION ---
app = FastAPI(title="Contact Intelligence Service", version="2.1")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Encryption Helper
def get_cipher_suite():
    if not ENCRYPTION_KEY:
        raise ValueError("CONTACT_ENCRYPTION_KEY env var is missing!")
    return Fernet(ENCRYPTION_KEY.encode())

def encrypt_text(text: str) -> str:
    cipher = get_cipher_suite()
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(token: str) -> str:
    cipher = get_cipher_suite()
    return cipher.decrypt(token.encode()).decode()

# --- MODELS ---
class MessageIngest(BaseModel):
    contact_name: str
    contact_telegram_id: Optional[int] = None
    contact_username: Optional[str] = None
    message_text: str
    channel: str = "telegram"
    timestamp: Optional[str] = None

class AnalysisResult(BaseModel):
    sentiment: str
    urgency: str
    topics: List[str]
    suggested_reply: Optional[str] = None

# --- BACKGROUND TASKS ---
async def process_ai_analysis(interaction_id: str, text: str, contact_id: str):
    """
    Analyzes message with FULL CONTEXT (No PII Scrubbing)
    """
    try:
        # 1. Generate Embeddings for Vector Search (Memory)
        emb_resp = await openai.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        embedding = emb_resp.data[0].embedding

        # 2. Analyze Content (Sentiment & Urgency)
        system_prompt = """
        You are a highly intelligent personal assistant. 
        Analyze the incoming message for:
        1. Sentiment (positive/neutral/negative)
        2. Urgency (low/medium/high/critical)
        3. Main topics
        4. Draft a short, style-matched reply if needed.
        
        Return JSON.
        """
        
        completion = await openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Message: {text}"}
            ],
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(completion.choices[0].message.content)
        
        # 3. Update Interaction in DB
        supabase.table("interactions").update({
            "embedding": embedding,
            "sentiment": analysis.get("sentiment"),
            "urgency": analysis.get("urgency"),
            "topics": analysis.get("topics", []),
            "message_metadata": analysis # Store full analysis JSON
        }).eq("id", interaction_id).execute()
        
        print(f"✅ Analyzed interaction {interaction_id}: {analysis.get('sentiment')}")

    except Exception as e:
        print(f"❌ Error in background analysis: {e}")

# --- ENDPOINTS ---

@app.post("/api/v1/contact/ingest")
async def ingest_message(payload: MessageIngest, background_tasks: BackgroundTasks):
    """
    Main entry point for n8n webhooks.
    1. Finds/Creates contact
    2. Encrypts & Saves message
    3. Triggers AI analysis background task
    """
    try:
        # 1. Find or Create Contact
        contact_query = supabase.table("contacts").select("id").eq("telegram_id", payload.contact_telegram_id).execute()
        
        if contact_query.data:
            contact_id = contact_query.data[0]['id']
        else:
            # Create new
            new_contact = supabase.table("contacts").insert({
                "name": payload.contact_name,
                "telegram_id": payload.contact_telegram_id,
                "telegram_username": payload.contact_username
            }).execute()
            contact_id = new_contact.data[0]['id']

        # 2. Encrypt Message (Security First!)
        encrypted_content = encrypt_text(payload.message_text)
        
        # 3. Save Interaction
        interaction = supabase.table("interactions").insert({
            "contact_id": contact_id,
            "channel": payload.channel,
            "direction": "incoming",
            "message_encrypted": encrypted_content, # Storing only encrypted!
            "timestamp": payload.timestamp or datetime.utcnow().isoformat()
        }).execute()
        
        interaction_id = interaction.data[0]['id']
        
        # 4. Trigger AI Analysis (Full Context)
        background_tasks.add_task(
            process_ai_analysis, 
            interaction_id, 
            payload.message_text, # Passing RAW text to AI (as requested)
            contact_id
        )
        
        return {"status": "success", "interaction_id": interaction_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "active", "mode": "FULL_CONTEXT_ENABLED"}
