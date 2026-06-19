import os
import json
import asyncio
import base64
import uuid
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog

# Internal imports
from agents.expense_agent import expense_agent
from config.settings import settings

# Setup logging
logger = structlog.get_logger(__name__)

app = FastAPI(title="Advanced Expense Compliance Agent API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuditRequest(BaseModel):
    merchant: str
    amount: float
    category: str
    description: Optional[str] = "Web submission"

@app.get("/health")
async def health():
    return {"status": "online", "model": settings.gemini_model}

@app.get("/policies")
async def get_policies():
    """Returns the actual policy database for the Policy Explorer."""
    from tools.expense_tools import POLICY_DATABASE
    return [{"category": k, "rule": v} for k, v in POLICY_DATABASE.items()]

@app.get("/stats")
async def get_stats():
    """Calculates real-time statistics from the audit logs."""
    import aiosqlite
    db_path = "audit_history.db"
    if not os.path.exists(db_path):
        return {"total_spent": 0, "total_saved": 0, "compliant_count": 0, "rejected_count": 0}
        
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        # Calculate totals
        async with db.execute("SELECT status, SUM(amount) as total, COUNT(*) as cnt FROM audit_logs GROUP BY status") as cursor:
            rows = await cursor.fetchall()
            stats = {"total_spent": 0, "total_saved": 0, "compliant_count": 0, "rejected_count": 0}
            for row in rows:
                if row["status"] == "COMPLIANT":
                    stats["total_spent"] += row["total"] or 0
                    stats["compliant_count"] = row["cnt"]
                else:
                    stats["total_saved"] += row["total"] or 0
                    stats["rejected_count"] += row["cnt"]
            return stats

@app.post("/audit")
async def audit_expense(
    merchant: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    description: str = Form(""),
    image: Optional[UploadFile] = File(None)
):
    """
    Advanced audit endpoint that handles both text and multimodal input.
    """
    user_id = "web_user_123" # In production, get from auth
    transaction_id = f"WEB_{uuid.uuid4().hex[:8]}"
    
    expense_data = {
        "transaction_id": transaction_id,
        "merchant_name": merchant,
        "amount": amount,
        "currency": "USD",
        "category": category,
        "description": description,
        "timestamp": "2024-06-19T10:00:00Z"
    }

    try:
        # If image is provided, we can pass it to the agent
        # NOTE: ADK Runner might need adjustment for multimodal, but we can simulate/extend it.
        # For now, let's process the text part via ADK and potentially handle the image separately if needed.
        
        # We will extend the process_expense to handle optional image data
        result = await expense_agent.process_expense(user_id, expense_data)
        
        # Add the transaction ID to the result for frontend tracking
        result["txn_id"] = transaction_id
        return result

    except Exception as e:
        logger.exception("api.audit_failure")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history():
    """
    Fetches the actual audit history from the persistent database.
    """
    import aiosqlite
    db_path = "audit_history.db"
    if not os.path.exists(db_path):
        return []
        
    try:
        async with aiosqlite.connect(db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 20") as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "id": row["id"],
                        "merchant": row["merchant"],
                        "amount": row["amount"],
                        "status": row["status"],
                        "reason": row["report"][:100] + "...",
                        "date": row["timestamp"].split("T")[0]
                    } for row in rows
                ]
    except Exception as e:
        logger.error("api.history_fetch_error", error=str(e))
        return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
