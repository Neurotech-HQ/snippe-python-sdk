"""Exceptions for Snippe SDK."""


class SnippeError(Exception):
    """Base exception for all Snippe errors."""

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
