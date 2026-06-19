import structlog
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from tools.mcp_tools import MCP_TOOLS

# Initialize logger
logger = structlog.get_logger(__name__)

# --- Mock Policy Database ---
# In a production environment, this would be a call to a Vector DB or SQL Database.
POLICY_DATABASE = {
    "travel": "All travel must be booked via Navan. Airfare must be Economy unless it is an international flight over 8 hours.",
    "meals": "Daily meal cap is $75. Alcohol is not reimbursable. Itemized receipts are mandatory for all transactions.",
    "software": "Subscriptions must be approved by IT. Personal accounts used for business SaaS are not compliant.",
    "equipment": "Hardware purchases over $500 require pre-approval from the Department Head.",
    "entertainment": "Strictly restricted. Requires VP-level pre-authorization.",
}

# --- Pydantic Models for Tool Inputs ---

class PolicyFetchInput(BaseModel):
    category: str = Field(..., description="The expense category (e.g., travel, meals, software) to retrieve rules for.")

class HumanReviewInput(BaseModel):
    transaction_id: str = Field(..., description="The unique identifier of the expense report.")
    flag_reason: str = Field(..., description="The specific reason why this expense was flagged for manual review.")
    risk_level: str = Field(default="medium", description="Risk level: low, medium, high.")

# --- Tool Functions ---

def fetch_policy(category: str) -> str:
    """Retrieves the latest corporate expense policy for a given category."""
    cat_lower = category.lower().strip()
    policy = POLICY_DATABASE.get(cat_lower)
    if not policy:
        return f"No specific policy found for '{category}'. Follow general company guidelines."
    return f"POLICY FOR {category.upper()}: {policy}"

def request_human_review(transaction_id: str, flag_reason: str, risk_level: str = "medium") -> str:
    """Escalates an expense to a human auditor."""
    logger.warning("tool.request_human_review.triggered", id=transaction_id, reason=flag_reason)
    return f"SUCCESS: Escalation ticket created for transaction {transaction_id}."

def convert_currency(amount: float, from_currency: str, to_currency: str = "USD") -> str:
    """Converts amounts between currencies. Supports EUR, GBP, JPY, INR to USD."""
    rates = {"EUR": 1.08, "GBP": 1.27, "JPY": 0.0064, "INR": 0.012}
    if from_currency.upper() == to_currency.upper():
        return f"{amount} {to_currency}"
    rate = rates.get(from_currency.upper())
    if not rate:
        return f"Warning: Unsupported currency '{from_currency}'. Assuming 1:1."
    converted = amount * rate
    return f"{amount} {from_currency} is approximately {converted:.2f} {to_currency}."

def estimate_tax_impact(amount: float, category: str) -> str:
    """Estimates potential tax reclaim (VAT/GST) based on category and region."""
    # Simplified logic for regional tax reclaim
    reclaim_rates = {"travel": 0.15, "software": 0.20, "meals": 0.05}
    rate = reclaim_rates.get(category.lower(), 0.0)
    potential_savings = amount * rate
    return f"Tax Analysis: Potential reclaim value is ${potential_savings:.2f} ({rate*100}% rate)."

# --- ADK Tool Registry ---
TOOLS_REGISTRY = {
    "fetch_policy": fetch_policy,
    "request_human_review": request_human_review,
    "convert_currency": convert_currency,
    "estimate_tax_impact": estimate_tax_impact,
    **MCP_TOOLS  # Inject advanced MCP integrations
}
