from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, field_validator, ValidationError
from typing import List, Optional, Any
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    google_api_key: SecretStr = Field(..., alias="GOOGLE_API_KEY")
    gemini_model: str = Field("gemini-2.0-flash", alias="GEMINI_MODEL")
    restricted_categories: List[str] = Field(default=[], alias="RESTRICTED_CATEGORIES")

    @field_validator("restricted_categories", mode="before")
    @classmethod
    def split_commas(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        extra="ignore"
    )

try:
    s = Settings()
    print("SUCCESS")
except ValidationError as e:
    print(e.json())
except Exception as e:
    print(f"OTHER ERROR: {e}")
