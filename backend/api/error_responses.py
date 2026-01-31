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

FORBIDDEN_403 = {
    "description": "Forbidden - Not authorized to access this resource",
    "content": {
        "application/json": {
            "example": {
                "error": "Unauthorized access to resource",
                "message": "You do not have permission to access this resource.",
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

USER_NOT_FOUND_404 = {
    "description": "Not Found - User does not exist",
    "content": {
        "application/json": {
            "example": {
                "error": "User with id {id} not found",
                "message": "User does not exist. Please create an account before logging in.",
            }
        }
    },
}

CONFLICT_409 = {
    "description": "Conflict - Resource already exists or constraint violation",
    "content": {
        "application/json": {
            "example": {
                "error": "Resource conflict",
                "message": "A resource with these details already exists",
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

STYTCH_SERVICE_ERROR_503 = {
    "description": "Service Unavailable - Authentication service error",
    "content": {
        "application/json": {
            "example": {
                "error": "Service unavailable",
                "message": "Authentication service is temporarily unavailable",
            }
        }
    },
}
