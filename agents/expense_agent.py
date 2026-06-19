import os
import structlog
import aiosqlite
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool

from tools.expense_tools import TOOLS_REGISTRY
from config.settings import settings
from config.prompts import EXPENSE_AUDIT_SYSTEM_PROMPT_TEMPLATE, ExpenseInput
from harness.security import security_harness

# Export API KEY
os.environ["GOOGLE_API_KEY"] = settings.google_api_key.get_secret_value()

logger = structlog.get_logger(__name__)

class ExpenseAgentOrchestrator:
    """
    Advanced orchestrator for the Expense Compliance Agent with Persistence and Multimodal readiness.
    """
    
    def __init__(self):
        logger.info("agent.init", name=settings.app_name)
        self.db_path = "audit_history.db"
        
        # 1. Define Advanced Tools from registry
        self.tools = [FunctionTool(func=f) for f in TOOLS_REGISTRY.values()]
        # Add internal state-specific tools if needed
        self.tools.append(FunctionTool(func=self.verify_merchant_reputation))
        
        # 2. Format System Prompt for Advanced Reasoning
        system_instruction = EXPENSE_AUDIT_SYSTEM_PROMPT_TEMPLATE.format(
            max_limit=settings.max_expense_limit,
            restricted_categories=", ".join(settings.restricted_categories)
        ) + "\n\nCRITICAL: Always use the 'verify_merchant_reputation' tool for transactions over $50."
        
        # 3. Initialize Core Agent
        self.agent = Agent(
            name=settings.app_name,
            model=settings.gemini_model,
            instruction=system_instruction,
            tools=self.tools
        )
        
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            session_service=self.session_service,
            app_name=settings.app_name,
            auto_create_session=True
        )

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    merchant TEXT,
                    amount REAL,
                    status TEXT,
                    report TEXT,
                    timestamp DATETIME
                )
            """)
            await db.commit()

    @staticmethod
    def verify_merchant_reputation(merchant_name: str) -> str:
        """Searches the web and corporate vendor lists to verify merchant credibility."""
        # Simulated "Advanced" tool logic
        if "apple" in merchant_name.lower() or "starbucks" in merchant_name.lower():
            return f"VERIFIED: {merchant_name} is a trusted premium vendor."
        return f"NEUTRAL: {merchant_name} is not on the high-risk blocklist, but is a new vendor."

    async def process_expense(self, user_id: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("agent.process_start", user_id=user_id)
        
        # Security Checks
        is_allowed, msg = security_harness.check_rate_limit(user_id)
        if not is_allowed: return {"status": "ERROR", "message": msg}
        
        expense, error = security_harness.validate_payload(ExpenseInput, raw_data)
        if error: return {"status": "ERROR", "message": error}
            
        threat_score = security_harness.analyze_threat(str(raw_data))
        if threat_score > 0.7:
            return {"status": "ERROR", "error": "MALICIOUS", "threat_score": threat_score}
            
        try:
            session_id = f"session_{user_id}"
            query = f"Audit this expense submission: {expense.model_dump_json()}"
            
            from google.genai import types
            user_message = types.Content(role="user", parts=[types.Part(text=query)])
            
            final_text = ""
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_message
            ):
                if event.content and event.content.parts:
                    for p in event.content.parts:
                        if p.text: final_text += p.text

            final_response = security_harness.sanitize_output(final_text)
            
            # Extract status from response (simplified heuristic for now)
            status = "COMPLIANT" if "COMPLIANT" in final_response.upper() else "FLAGGED"
            
            # Save to Database
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO audit_logs VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (expense.transaction_id, user_id, expense.merchant_name, expense.amount, status, final_response, datetime.now().isoformat())
                )
                await db.commit()

            return {
                "status": "SUCCESS",
                "audit_report": final_response,
                "metadata": {"session_id": session_id, "threat_score": threat_score}
            }
            
        except Exception as e:
            logger.exception("agent.failure")
            return {"status": "ERROR", "message": str(e)}

# Instantiate
expense_agent = ExpenseAgentOrchestrator()
# Run DB initialization in a background task or on first call
import asyncio
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(expense_agent.init_db())
    else:
        loop.run_until_complete(expense_agent.init_db())
except Exception:
    pass
