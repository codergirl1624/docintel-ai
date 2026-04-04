import os
import secrets
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """Validate incoming API key against environment variable."""
    
    expected_key = os.getenv("DOCINTEL_API_KEY")

    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured on server.",
        )

    if not api_key or not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing API key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key