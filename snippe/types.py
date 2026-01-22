"""Type definitions for Snippe SDK."""

from typing import Literal

PaymentType = Literal["mobile", "card", "dynamic-qr"]
PaymentStatus = Literal["pending", "completed", "failed", "expired", "voided"]
Currency = Literal["TZS", "KES", "UGX"]
WebhookEvent = Literal[
    "payment.completed",
    "payment.failed",
    "payment.expired",
    "payment.voided"
]
