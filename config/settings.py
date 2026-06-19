import os
from pathlib import Path
from typing import List, Optional, Union, Any
from pydantic import Field, SecretStr, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """
    Application settings for the Expense Compliance Agent.
    """
    google_api_key: SecretStr = Field(..., validation_alias=AliasChoices("GOOGLE_API_KEY", "google_api_key"))
    
    # Using the latest model found in the user's current environment (June 2026)
    gemini_model: str = Field("gemini-2.5-flash", validation_alias=AliasChoices("GEMINI_MODEL", "gemini_model"))
    
    app_name: str = "ExpenseComplianceAgent"
    env: str = Field("development", validation_alias=AliasChoices("ENV", "env"))
    debug: bool = Field(True, validation_alias=AliasChoices("DEBUG", "debug"))
    log_level: str = Field("INFO", validation_alias=AliasChoices("LOG_LEVEL", "log_level"))
    
    max_expense_limit: float = Field(100.0, validation_alias=AliasChoices("MAX_EXPENSE_LIMIT", "max_expense_limit"))
    
    restricted_categories_raw: str = Field(
        "gambling,entertainment,personal_care", 
        validation_alias=AliasChoices("RESTRICTED_CATEGORIES", "restricted_categories")
    )
    
    trusted_domains_raw: str = Field(
        "google.com,github.com", 
        validation_alias=AliasChoices("TRUSTED_DOMAINS", "trusted_domains")
    )
    
    enable_pii_redaction: bool = Field(True, validation_alias=AliasChoices("ENABLE_PII_REDACTION", "enable_pii_redaction"))

    @property
    def restricted_categories(self) -> List[str]:
        return [cat.strip() for cat in self.restricted_categories_raw.split(",") if cat.strip()]

    @property
    def trusted_domains(self) -> List[str]:
        return [dom.strip() for dom in self.trusted_domains_raw.split(",") if dom.strip()]

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

# Singleton instance
settings = Settings()
