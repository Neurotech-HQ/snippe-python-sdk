"""
Snippe - Python SDK for Snippe Payment API.

Accept payments via mobile money, card, and QR code.

Usage:
    >>> from snippe import Snippe, Customer
    >>> client = Snippe("your_api_key")
    >>> payment = client.create_mobile_payment(
    ...     amount=1000,
    ...     currency="TZS",
    ...     phone_number="0788500000",
    ...     customer=Customer(firstname="John", lastname="Doe")
    ... )
    >>> print(payment.reference)
"""

from .client import AsyncSnippe, Snippe
from .exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    SnippeError,
    ValidationError,
    WebhookVerificationError,
    ConflictError,
    ForbiddenError,
    UnprocessableEntityError
)

from .models import (
    Balance,
    Customer,
    Payment,
    PaymentDetails,
    PaymentList,
    WebhookPayload,
    Payout,
    PayoutList,
    PayoutFee,
    PayoutRecipient,
    PayoutChannel,
    PayoutAmount,

)

from .types import Currency, PaymentStatus, PaymentType, WebhookEvent
from .webhooks import WebhookHandler, verify_webhook

__version__ = "0.1.0"
__all__ = [
    # Clients
    "Snippe",
    "AsyncSnippe",
    # Models
    "Customer",
    "Payment",
    "PaymentDetails",
    "PaymentList",
    "Balance",
    "WebhookPayload",
    # Types
    "PaymentType",
    "PaymentStatus",
    "Currency",
    "WebhookEvent",
    # Webhooks
    "WebhookHandler",
    "verify_webhook",
    # Exceptions
    "SnippeError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "WebhookVerificationError",
    "ForbiddenError", 
    "ConflictError",
    "UnprocessableEntityError",
    #payouts
    "Payout",
    "PayoutList", 
    "PayoutFee",
    "PayoutRecipient",
    "PayoutChannel",
    "PayoutAmount",
]
