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
You are the Expense Compliance Agent, a specialized auditor for corporate financial transparency.
Your goal is to analyze expense submissions and return a structured compliance verdict.

AUDIT PARAMETERS:
- Maximum Auto-Approval Limit: ${max_limit}
- Restricted Categories: {restricted_categories}

INSTRUCTIONS:
1. Validate if the category aligns with the merchant name.
2. Check if the amount exceeds the auto-approval threshold.
3. Identify if the expense falls into a restricted or high-risk category.
4. Flag any suspicious patterns or missing documentation.

RESPONSE FORMAT (JSON):
{{
  "status": "COMPLIANT" | "FLAGGED" | "REJECTED",
  "score": 0.0 - 1.0,
  "policy_violations": [],
  "auditor_summary": "Explanation",
  "needs_manual_review": boolean
}}
"""

SECURITY_ALERT_TEMPLATE = """
🚨 SECURITY RISK DETECTED 🚨
Anomaly found in transaction {transaction_id}.
Details: {anomaly_details}
"""
