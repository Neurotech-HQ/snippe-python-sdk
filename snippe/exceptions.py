"""Exceptions for Snippe SDK."""


class SnippeError(Exception):
    """Base exception for all Snippe errors.

    All exceptions raised by the SDK inherit from this class.
    
    Args:
        message: Human-readable error description
        code: HTTP status code from the API response (if applicable)
        error_code: Snippe-specific error code for detailed debugging
    
    Example:
        >>> from snippe import SnippeError
        >>> try:
        ...     client.create_mobile_payment(...)
        ... except SnippeError as e:
        ...     print(f"Error: {e.message}")
        ...     print(f"HTTP Code: {e.code}")
        ...     print(f"Snippe Code: {e.error_code}")
    
    """

    def __init__(self, message: str, code: int = 0, error_code: str = ""):
        self.message = message
        self.code = code
        self.error_code = error_code
        super().__init__(message)


class AuthenticationError(SnippeError):
    """Invalid or missing API key."""
    pass


class ValidationError(SnippeError):
    """Invalid request parameters."""
    pass


class NotFoundError(SnippeError):
    """Resource not found."""
    pass


class RateLimitError(SnippeError):
    """Too many requests."""
    pass


class ServerError(SnippeError):
    """Snippe server error."""
    pass


class WebhookVerificationError(SnippeError):
    """Invalid webhook signature."""
    pass


class ForbiddenError(SnippeError):
    """Authenticated but not authorized to access resource (403)."""
    pass


class ConflictError(SnippeError):
    """Resource already exists or state conflict (409)."""
    pass


class UnprocessableEntityError(SnippeError):
    """Idempotency key mismatch or validation error (422)."""
    pass