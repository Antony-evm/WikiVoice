"""Reusable OpenAPI error response definitions for FastAPI endpoints.

These are mapped to the custom exception classes and can be referenced
in endpoint decorators using the responses parameter.
"""

UNAUTHORIZED_401 = {
    "description": "Unauthorized - Invalid or expired session token",
    "content": {
        "application/json": {
            "example": {
                "error": "Invalid session token",
                "message": "The session has expired, please log in again.",
            }
        }
    },
}

NOT_FOUND_404 = {
    "description": "Not Found - Resource does not exist",
    "content": {
        "application/json": {
            "example": {
                "error": "Resource not found",
                "message": "The requested resource does not exist",
            }
        }
    },
}

USER_EXISTS_409 = {
    "description": "Conflict - User with this email or Stytch ID already exists",
    "content": {
        "application/json": {
            "example": {
                "error": "User already exists",
                "message": "A user with this email address already exists",
            }
        }
    },
}

VALIDATION_ERROR_422 = {
    "description": "Validation Error - Invalid input data",
    "content": {
        "application/json": {
            "example": {
                "detail": [
                    {
                        "loc": ["body", "field_name"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            }
        }
    },
}

INSUFFICIENT_ANSWERS_400 = {
    "description": "Bad Request - Insufficient answers provided",
    "content": {
        "application/json": {
            "example": {
                "error": "Insufficient answers",
                "message": "Please answer all required questions before completing",
            }
        }
    },
}

DATABASE_ERROR_500 = {
    "description": "Internal Server Error - Database error",
    "content": {
        "application/json": {
            "example": {
                "error": "Database error",
                "message": "An error occurred while accessing the database",
            }
        }
    },
}

INTERNAL_SERVER_ERROR_500 = {
    "description": "Internal Server Error",
    "content": {
        "application/json": {
            "example": {
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again later.",
            }
        }
    },
}
