import re
import time
import structlog
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, ValidationError

# Initialize logger
logger = structlog.get_logger(__name__)

class SecurityHarness:
    """
    Middleware-like security layer for the Expense Compliance Agent.
    Handles threat detection, rate limiting, and data sanitization.
    """
    
    def __init__(self):
        # In-memory rate limiting store: {user_id: [timestamps]}
        self._rate_limit_cache: Dict[str, List[float]] = {}
        self.LIMIT_WINDOW = 60  # 1 minute
        self.MAX_REQUESTS = 15  # per window
        
        # Simple heuristic patterns for prompt injection
        self._injection_patterns = [
            r"ignore (all )?previous instructions",
            r"system prompt",
            r"you are now a",
            r"new role:",
            r"reveal your (internal|secret)",
            r"bash:",
            r"sudo ",
            r"eval\(",
            r"<script>",
        ]

    def check_rate_limit(self, user_id: str) -> Tuple[bool, str]:
        """
        Validates if the user is within their allowed request quota.
        """
        now = time.time()
        if user_id not in self._rate_limit_cache:
            self._rate_limit_cache[user_id] = []
            
        # Clear expired timestamps
        self._rate_limit_cache[user_id] = [
            t for t in self._rate_limit_cache[user_id] 
            if now - t < self.LIMIT_WINDOW
        ]
        
        if len(self._rate_limit_cache[user_id]) >= self.MAX_REQUESTS:
            logger.error("security.rate_limit_exceeded", user_id=user_id)
            return False, "Rate limit exceeded. Please try again in a minute."
            
        self._rate_limit_cache[user_id].append(now)
        return True, ""

    def analyze_threat(self, input_text: str) -> float:
        """
        Scans input for prompt injection and malicious patterns.
        Returns a threat score between 0.0 (safe) and 1.0 (malicious).
        """
        score = 0.0
        matches = []
        
        for pattern in self._injection_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                score += 0.35
                matches.append(pattern)
                
        if score > 0:
            logger.warning("security.threat_detected", 
                           score=round(score, 2), 
                           patterns=matches)
            
        return min(score, 1.0)

    def validate_payload(self, model: BaseModel, data: dict) -> Tuple[Optional[BaseModel], Optional[str]]:
        """
        Strict validation of data against Pydantic models.
        """
        try:
            validated_data = model(**data)
            return validated_data, None
        except ValidationError as e:
            logger.error("security.validation_error", errors=e.json())
            return None, f"Invalid data format: {str(e)}"

    def sanitize_output(self, raw_output: str) -> str:
        """
        Sanitizes agent output to prevent leakage of internal IDs, 
        confidential instructions, or PII.
        """
        # Redact potential API keys (generic pattern)
        sanitized = re.sub(r"AIza[0-9A-Za-z-_]{35}", "[REDACTED_API_KEY]", raw_output)
        
        # Redact potential internal project paths
        sanitized = re.sub(r"(/[a-zA-Z0-9_-]+)+/expense_compliance_agent", "[INTERNAL_ROOT]", sanitized)
        
        # Check for system prompt leaks (heuristic)
        if "You are the Expense Compliance Agent" in sanitized:
            logger.critical("security.prompt_leak_detected")
            return "Error: Internal system state detected in output. Output blocked."
            
        return sanitized

# Singleton instance
security_harness = SecurityHarness()
