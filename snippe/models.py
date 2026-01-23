"""Data models for Snippe SDK."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .types import Currency, PaymentStatus, PaymentType, WebhookEvent


@dataclass
class Customer:
    """Customer information."""
    firstname: str
    lastname: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        data = {"firstname": self.firstname, "lastname": self.lastname}
        if self.email:
            data["email"] = self.email
        if self.address:
            data["address"] = self.address
        if self.city:
            data["city"] = self.city
        if self.state:
            data["state"] = self.state
        if self.postcode:
            data["postcode"] = self.postcode
        if self.country:
            data["country"] = self.country
        return data


@dataclass
class PaymentDetails:
    """Payment amount details."""
    amount: int
    currency: Currency
    callback_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        data = {"amount": self.amount, "currency": self.currency}
        if self.callback_url:
            data["callback_url"] = self.callback_url
        return data


@dataclass
class Payment:
    """Payment response from API."""
    reference: str
    status: PaymentStatus
    amount: int
    currency: Currency
    payment_type: PaymentType
    expires_at: Optional[str] = None
    payment_url: Optional[str] = None
    qr_code: Optional[str] = None
    payment_qr_code: Optional[str] = None
    payment_token: Optional[str] = None
    id: Optional[str] = None
    psp_reference: Optional[str] = None
    fee_amount: Optional[int] = None
    net_amount: Optional[int] = None
    customer: Optional[dict] = None
    metadata: Optional[dict] = None
    created_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Payment":
        """Create Payment from API response dict."""
        # Handle nested amount structure from some API responses
        amount_data = data.get("amount")
        if isinstance(amount_data, dict):
            amount = amount_data.get("value", 0)
            currency = amount_data.get("currency", data.get("currency", "TZS"))
        else:
            amount = amount_data if amount_data is not None else 0
            currency = data.get("currency", "TZS")

        return cls(
            reference=data.get("reference", ""),
            status=data.get("status", "pending"),
            amount=amount,
            currency=currency,
            payment_type=data.get("payment_type", ""),
            expires_at=data.get("expires_at"),
            payment_url=data.get("payment_url"),
            qr_code=data.get("qr_code"),
            payment_qr_code=data.get("payment_qr_code"),
            payment_token=data.get("payment_token"),
            id=data.get("id"),
            psp_reference=data.get("psp_reference"),
            fee_amount=data.get("fee_amount"),
            net_amount=data.get("net_amount"),
            customer=data.get("customer"),
            metadata=data.get("metadata"),
            created_at=data.get("created_at"),
        )


@dataclass
class PaymentList:
    """Paginated list of payments."""
    payments: list[Payment]
    limit: int
    offset: int

    @classmethod
    def from_dict(cls, data: dict) -> "PaymentList":
        """Create PaymentList from API response dict."""
        return cls(
            payments=[Payment.from_dict(p) for p in data.get("payments", [])],
            limit=data.get("limit", 20),
            offset=data.get("offset", 0),
        )


@dataclass
class Balance:
    """Account balance."""
    available_balance: int
    balance: int
    currency: Currency

    @classmethod
    def from_dict(cls, data: dict) -> "Balance":
        """Create Balance from API response dict."""
        return cls(
            available_balance=data.get("available_balance", 0),
            balance=data.get("balance", 0),
            currency=data.get("currency", "TZS"),
        )


@dataclass
class WebhookPayload:
    """Webhook event payload."""
    event: WebhookEvent
    reference: str
    status: PaymentStatus
    amount: dict
    payment_channel: str
    payment_fee: int
    customer: dict
    metadata: dict
    completed_at: Optional[str]
    created_at: str
    timestamp: int

    @classmethod
    def from_dict(cls, data: dict) -> "WebhookPayload":
        """Create WebhookPayload from webhook data."""
        return cls(
            event=data["event"],
            reference=data["reference"],
            status=data["status"],
            amount=data["amount"],
            payment_channel=data.get("payment_channel", ""),
            payment_fee=data.get("payment_fee", 0),
            customer=data.get("customer", {}),
            metadata=data.get("metadata", {}),
            completed_at=data.get("completed_at"),
            created_at=data["created_at"],
            timestamp=data["timestamp"],
        )
