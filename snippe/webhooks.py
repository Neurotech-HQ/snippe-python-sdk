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

    Verifies HMAC-SHA256 signatures and prevents replay attacks using timestamps.

    Args:
        signing_key: Your webhook signing key from the Snippe dashboard
        tolerance: Max age in seconds for webhook (default: 300 seconds / 5 minutes)

    Usage:
        >>> from snippe import WebhookHandler
        >>> handler = WebhookHandler("your_webhook_signing_key")
        >>> 
        >>> # In your webhook endpoint
        >>> payload = handler.verify_and_parse(
        ...     body=request.body.decode(),
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
            signing_key: Your webhook signing key from the Snippe dashboard
            tolerance: Max age in seconds for webhook (default: 5 minutes)
                    Prevents replay attacks by rejecting old webhooks
        """
        self.signing_key = signing_key
        self.tolerance = tolerance

    def compute_signature(self, payload: str, timestamp: str) -> str:
        """
        Combines timestamp and payload with a dot, then signs with the signing key.

        Args:
            payload: Raw request body as string
            timestamp: Unix timestamp from X-Webhook-Timestamp header

        Returns:
            Hex-encoded HMAC-SHA256 signature

        Example:
            >>> signature = handler.compute_signature(
            ...     payload='{"event":"payment.completed"}',
            ...     timestamp="1700000000"
            ... )
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
            True if signature is valid and timestamp is fresh

        Raises:
            WebhookVerificationError: If signature is invalid or timestamp expired
        
        Example:
            >>> try:
            ...     handler.verify_signature(
            ...         body=request.body.decode(),
            ...         signature=request.headers["X-Webhook-Signature"],
            ...         timestamp=request.headers["X-Webhook-Timestamp"]
            ...     )
            ...     print("Webhook verified")
            ... except WebhookVerificationError as e:
            ...     print(f"Verification failed: {e}")
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

        Use this if you've already verified the signature separately.
        Converts the webhook JSON data into a WebhookPayload object.

        Args:
            data: Parsed JSON payload from webhook

        Returns:
            WebhookPayload object with typed fields

        Example:
            >>> # If you verified manually
            >>> data = json.loads(request.body)
            >>> payload = handler.parse(data)
            >>> if payload.event == "payment.completed":
            ...     print(f"Payment {payload.reference} completed")
        """
        return WebhookPayload.from_dict(data)

    def verify_and_parse(
        self,
        body: str,
        signature: str,
        timestamp: str,
    ) -> WebhookPayload:
        """
        Verify signature and parse webhook payload in one step.

        This is the main method you'll use in your webhook endpoint.
        Verifies the signature, then parses the payload.

        Args:
            body: Raw request body as string
            signature: Value from X-Webhook-Signature header
            timestamp: Value from X-Webhook-Timestamp header

        Returns:
            WebhookPayload object

        Raises:
            WebhookVerificationError: If signature is invalid or timestamp expired

        Example:
            >>> from snippe import WebhookHandler
            >>> 
            >>> handler = WebhookHandler("your_webhook_signing_key")
            >>> 
            >>> # In your Flask/FastAPI/Django endpoint
            >>> @app.post("/webhooks/snippe")
            ... def webhook(request):
            ...     try:
            ...         payload = handler.verify_and_parse(
            ...             body=request.body.decode(),
            ...             signature=request.headers["X-Webhook-Signature"],
            ...             timestamp=request.headers["X-Webhook-Timestamp"]
            ...         )
            ...         
            ...         if payload.event == "payment.completed":
            ...             # Update order status
            ...             order_id = payload.metadata.get("order_id")
            ...             print(f"Order {order_id} paid")
            ...         
            ...         return {"status": "ok"}
            ...         
            ...     except WebhookVerificationError as e:
            ...         return {"error": str(e)}, 400
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

    This is a one-liner alternative to using the WebhookHandler class.
    Creates a temporary handler and verifies the webhook in one step.

    Args:
        body: Raw request body as string
        signature: Value from X-Webhook-Signature header
        timestamp: Value from X-Webhook-Timestamp header
        signing_key: Your webhook signing key
        tolerance: Max age in seconds (default: 5 minutes)

    Returns:
        WebhookPayload object

    Raises:
        WebhookVerificationError: If signature is invalid or timestamp expired
    
    Example:
        >>> from snippe import verify_webhook, WebhookVerificationError
        >>> 
        >>> try:
        ...     payload = verify_webhook(
        ...         body=request.body.decode(),
        ...         signature=request.headers["X-Webhook-Signature"],
        ...         timestamp=request.headers["X-Webhook-Timestamp"],
        ...         signing_key="your_webhook_signing_key"
        ...     )
        ...     
        ...     if payload.event == "payment.completed":
        ...         print(f"Payment {payload.reference} completed!")
        ...         
        ... except WebhookVerificationError as e:
        ...     print(f"Invalid webhook: {e}")
    """
    handler = WebhookHandler(signing_key, tolerance)
    return handler.verify_and_parse(body, signature, timestamp)
