"""Webhook verification utilities for Snippe SDK."""

import hashlib
import hmac
import time
from typing import Optional

from .exceptions import WebhookVerificationError
from .models import WebhookPayload


class WebhookHandler:
    """
    Webhook handler for verifying and parsing Snippe webhooks.

    Usage:
        >>> from snippe import WebhookHandler
        >>> handler = WebhookHandler("your_webhook_signing_key")
        >>> payload = handler.verify_and_parse(
        ...     body=request.body,
        ...     signature=request.headers["X-Webhook-Signature"],
        ...     timestamp=request.headers["X-Webhook-Timestamp"]
        ... )
    """

    def __init__(
        self,
        signing_key: str,
        tolerance: int = 300,
    ):
        """
        Initialize webhook handler.

        Args:
            signing_key: Your webhook signing key
            tolerance: Max age in seconds for webhook (default: 5 minutes)
        """
        self.signing_key = signing_key
        self.tolerance = tolerance

    def compute_signature(self, payload: str, timestamp: str) -> str:
        """
        Compute HMAC-SHA256 signature for payload.

        Args:
            payload: Raw request body as string
            timestamp: Unix timestamp from X-Webhook-Timestamp header

        Returns:
            Hex-encoded signature
        """
        message = f"{timestamp}.{payload}"
        signature = hmac.new(
            self.signing_key.encode(),
            message.encode(),
            hashlib.sha256,
        )
        return signature.hexdigest()

    def verify_signature(
        self,
        payload: str,
        signature: str,
        timestamp: str,
    ) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: Raw request body as string
            signature: Value from X-Webhook-Signature header
            timestamp: Value from X-Webhook-Timestamp header

        Returns:
            True if signature is valid

        Raises:
            WebhookVerificationError: If signature is invalid or expired
        """
        # Check timestamp to prevent replay attacks
        try:
            ts = int(timestamp)
        except (ValueError, TypeError):
            raise WebhookVerificationError("Invalid timestamp")

        if abs(time.time() - ts) > self.tolerance:
            raise WebhookVerificationError("Webhook timestamp expired")

        # Compute and compare signatures
        expected = self.compute_signature(payload, timestamp)
        if not hmac.compare_digest(expected, signature):
            raise WebhookVerificationError("Invalid signature")

        return True

    def parse(self, data: dict) -> WebhookPayload:
        """
        Parse webhook payload without verification.

        Args:
            data: Parsed JSON payload

        Returns:
            WebhookPayload object
        """
        return WebhookPayload.from_dict(data)

    def verify_and_parse(
        self,
        body: str,
        signature: str,
        timestamp: str,
    ) -> WebhookPayload:
        """
        Verify signature and parse webhook payload.

        Args:
            body: Raw request body as string
            signature: Value from X-Webhook-Signature header
            timestamp: Value from X-Webhook-Timestamp header

        Returns:
            WebhookPayload object

        Raises:
            WebhookVerificationError: If signature is invalid or expired
        """
        import json

        self.verify_signature(body, signature, timestamp)
        data = json.loads(body)
        return self.parse(data)


def verify_webhook(
    body: str,
    signature: str,
    timestamp: str,
    signing_key: str,
    tolerance: int = 300,
) -> WebhookPayload:
    """
    Convenience function to verify and parse a webhook.

    Args:
        body: Raw request body as string
        signature: Value from X-Webhook-Signature header
        timestamp: Value from X-Webhook-Timestamp header
        signing_key: Your webhook signing key
        tolerance: Max age in seconds (default: 5 minutes)

    Returns:
        WebhookPayload object

    Raises:
        WebhookVerificationError: If signature is invalid or expired
    """
    handler = WebhookHandler(signing_key, tolerance)
    return handler.verify_and_parse(body, signature, timestamp)
