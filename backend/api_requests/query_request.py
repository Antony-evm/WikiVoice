"""Query request models."""

import re
from typing import Literal

from pydantic import BaseModel, field_validator

MAX_QUERY_LENGTH = 2000
MIN_QUERY_LENGTH = 1

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+|the\s+)?(previous|above)\s+instructions",
    r"disregard\s+(all\s+|the\s+)?(previous|above)",
    r"forget\s+(all\s+|the\s+)?(previous|above)",
    r"you\s+are\s+now\s+(a|an)",
    r"new\s+instructions:",
    r"system\s*:\s*",
]


class QueryRequest(BaseModel):
    """Request to submit a query with validation."""

    session_id: int
    query_text: str
    input_mode: Literal["text", "voice"] = "text"

    @field_validator("query_text")
    @classmethod
    def validate_query_text(cls, v: str) -> str:
        """Validate and sanitize query text."""
        v = v.strip()

        if len(v) < MIN_QUERY_LENGTH:
            msg = "Query cannot be empty"
            raise ValueError(msg)
        if len(v) > MAX_QUERY_LENGTH:
            msg = f"Query exceeds maximum length of {MAX_QUERY_LENGTH} characters"
            raise ValueError(msg)

        lower_text = v.lower()
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, lower_text, re.IGNORECASE):
                msg = "Query contains disallowed content"
                raise ValueError(msg)

        return v
