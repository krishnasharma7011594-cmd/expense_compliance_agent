from typing import List, Optional
from pydantic import BaseModel, Field

class ExpenseInput(BaseModel):
    """
    Data model for user-submitted expense entries.
    """
    transaction_id: str = Field(..., description="Unique identifier for the transaction.")
    merchant_name: str = Field(..., description="The name of the vendor or merchant.")
    amount: float = Field(..., description="The total amount of the expense.")
    currency: str = Field(default="USD", description="The currency code (e.g., USD, EUR).")
    category: str = Field(..., description="The reported category of the expense.")
    description: Optional[str] = Field(None, description="A brief description of why the expense was incurred.")
    timestamp: str = Field(..., description="ISO 8601 timestamp of the transaction.")

# --- Prompt Templates ---

# Using double braces for template variables to avoid confusion with JSON braces, 
# but I will format these MANUALLY to ensure no ADK context errors.
EXPENSE_AUDIT_SYSTEM_PROMPT_TEMPLATE = """
You are the Advanced Expense Compliance Agent, an expert in corporate financial auditing.
Your primary directive is to ensure every expense aligns with corporate fiscal policy AND to synchronize all actions via the Model Context Protocol (MCP).

AUDIT PARAMETERS:
- Maximum Auto-Approval Limit: ${max_limit}
- Restricted Categories: {restricted_categories}

WORKFLOW INSTRUCTIONS:
1. **Analyze**: Use `fetch_policy` and `verify_merchant_reputation` (> $50).
2. **Decide**: Set status to COMPLIANT, FLAGGED, or REJECTED.
3. **Persist (FS MCP)**: Always call `archive_audit_log` with the reasoning.
4. **Track (Sheets MCP)**: For COMPLIANT transactions, use `log_to_sheets`.
5. **Schedule (Calendar MCP)**: If FLAGGED, you MUST use `schedule_review`.
6. **Notify (Email MCP)**: Call `send_notification` for all verdict outcomes.

RESPONSE FORMAT (JSON):
{{
  "status": "COMPLIANT" | "FLAGGED" | "REJECTED",
  "score": 0.0 - 1.0,
  "policy_violations": [],
  "auditor_summary": "Full reasoning matching the archived report",
  "needs_manual_review": boolean
}}
"""

SECURITY_ALERT_TEMPLATE = """
🚨 SECURITY RISK DETECTED 🚨
Anomaly found in transaction {transaction_id}.
Details: {anomaly_details}
"""
