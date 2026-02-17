"""Data models for Snippe SDK."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .types import (
    Currency, 
    PaymentStatus, 
    PaymentType, 
    WebhookEvent,
    PayoutChannel as PayoutChannelType,
    PayoutStatus as PayoutStatusType,
    PayoutProvider,
    BankCode
)


@dataclass
class Customer:
    """Customer information.
    Args:
        firstname: Customer's first name (required)
        lastname: Customer's last name (required)
        email: Customer's email address (optional)
        address: Street address (optional, recommended for card payments)
        city: City (optional, recommended for card payments)
        state: State or region (optional)
        postcode: Postal code (optional)
        country: Country code (optional, e.g., "TZ" for Tanzania)
        phone: Customer's phone number (optional)
    
    Example:
        >>> customer = Customer(
        ...     firstname="John",
        ...     lastname="Doe",
        ...     email="john@example.com",
        ...     phone="0712345678"
        ... )
    """
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
    """Payment amount details.
    
    Args:
        amount: Amount in smallest currency unit (e.g., 1000 = 1000 TZS)
        currency: Currency code (TZS, KES, UGX)
        callback_url: URL to redirect after payment (optional)
    
    Example:
        >>> details = PaymentDetails(
        ...     amount=5000,
        ...     currency="TZS",
        ...     callback_url="https://myapp.com/callback"
        ... )

    """
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
    """Payment response from API.

    Args:
        reference: Unique payment reference for status checks
        status: Current payment status (pending, completed, failed, expired, voided)
        amount: Amount in smallest currency unit
        currency: Currency code (TZS, KES, UGX)
        payment_type: Type of payment (mobile, card, dynamic-qr)
        expires_at: When the payment expires (ISO 8601 timestamp)
        payment_url: URL for card payment redirect
        qr_code: QR code data (legacy field)
        payment_qr_code: Base64-encoded QR code image for QR payments
        payment_token: Token embedded in QR code
        id: Internal payment ID
        psp_reference: Payment Service Provider reference
        fee_amount: Transaction fee amount
        net_amount: Amount after fees
        customer: Customer information as dict
        metadata: Custom key-value pairs from request
        created_at: Creation timestamp (ISO 8601)
    
    Example:
        >>> payment = client.create_mobile_payment(...)
        >>> print(f"Ref: {payment.reference}, Status: {payment.status}")
        >>> if payment.payment_qr_code:
        ...     # Display QR code to customer
        ...     pass
    
    """
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
    """Paginated list of payments.

    Args:
        payments: List of Payment objects
        limit: Number of results per page requested
        offset: Pagination offset used
    
    Example:
        >>> result = client.list_payments(limit=10, offset=0)
        >>> print(f"Showing {len(result.payments)} payments")
        >>> for payment in result.payments:
        ...     print(f"{payment.reference}: {payment.status}")
    
    """
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
    """Account balance.

    Args:
        available_balance: Amount available for withdrawal/use
        balance: Total account balance (including pending)
        currency: Currency code (TZS, KES, UGX)
    
    Example:
        >>> balance = client.get_balance()
        >>> print(f"Available: {balance.available_balance} {balance.currency}")
        >>> print(f"Total: {balance.balance} {balance.currency}")
    
    """
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
    """Webhook event payload.

    Args:
        event: Webhook event type (payment.completed, payment.failed, etc.)
        reference: Payment reference
        status: Payment status
        amount: Amount details as dict (value and currency)
        payment_channel: Channel used for payment (e.g., "M-PESA", "CARD")
        payment_fee: Fee charged for the transaction
        customer: Customer information as dict
        metadata: Custom key-value pairs from request
        completed_at: When payment completed (if applicable)
        created_at: When payment was created
        timestamp: Webhook timestamp for verification
    
    Example:
        >>> payload = verify_webhook(body, signature, timestamp, signing_key)
        >>> if payload.event == "payment.completed":
        ...     print(f"Payment {payload.reference} completed!")
        ...     print(f"Channel: {payload.payment_channel}")
        ...     print(f"Fee: {payload.payment_fee}")
    """
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


@dataclass
class PayoutRecipient:
    """Recipient information for payouts.
    
    Args:
        name: Full name of recipient
        phone: Phone number for mobile money payouts (format: 255XXXXXXXXX)
        bank: Bank code for bank transfers (e.g., "CRDB", "NMB")
        account: Bank account number for bank transfers
    
    Example for mobile:
        >>> recipient = PayoutRecipient(
        ...     name="John Doe",
        ...     phone="255712345678"
        ... )
    
    Example for bank:
        >>> recipient = PayoutRecipient(
        ...     name="John Doe",
        ...     bank="CRDB",
        ...     account="0211049375"
        ... )
    """
    name: str
    phone: Optional[str] = None
    bank: Optional[BankCode] = None
    account: Optional[str] = None


@dataclass
class PayoutChannel:
    """Channel information for payout.
    
    Args:
        type: Channel type (mobile or bank)
        provider: Provider code (airtel, tigo, halopesa, or bank)
    
    Example:
        >>> channel = PayoutChannel(
        ...     type="mobile",
        ...     provider="airtel"
        ... )
    """
    type: PayoutChannelType
    provider: PayoutProvider


@dataclass
class PayoutAmount:
    """Amount details for payout.
    
    Args:
        value: Amount in smallest currency unit
        currency: Currency code (TZS, KES, UGX)
    
    Example:
        >>> amount = PayoutAmount(
        ...     value=5000,
        ...     currency="TZS"
        ... )
    """
    value: int
    currency: Currency


@dataclass
class Payout:
    """Payout response from API.
    
    Args:
        reference: Unique payout reference
        status: Payout status (pending, completed, failed, reversed)
        amount: Payout amount details
        fees: Fee amount details
        total: Total amount deducted (amount + fees)
        channel: Channel information
        recipient: Recipient information
        narration: Description/reason for payout
        created_at: Creation timestamp (ISO 8601)
        completed_at: Completion timestamp (ISO 8601, if completed)
        external_reference: Provider's reference number
        id: Internal payout ID
        metadata: Custom key-value pairs from request
        source: Source of payout (api, dashboard)
        failure_reason: Reason for failure (if status failed)
    
    Example:
        >>> payout = client.create_mobile_payout(...)
        >>> print(f"Reference: {payout.reference}")
        >>> print(f"Status: {payout.status}")
        >>> print(f"Amount: {payout.amount.value} {payout.amount.currency}")
    """
    reference: str
    status: PayoutStatusType
    amount: PayoutAmount
    fees: PayoutAmount
    total: PayoutAmount
    channel: PayoutChannel
    recipient: PayoutRecipient
    narration: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    external_reference: Optional[str] = None
    id: Optional[str] = None
    metadata: Optional[dict] = None
    source: Optional[str] = None
    failure_reason: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Payout":
        """Create Payout from API response dict."""
        # Handle nested amount structure
        amount_data = data.get("amount", {})
        fees_data = data.get("fees", {})
        total_data = data.get("total", {})
        
        # Handle channel data
        channel_data = data.get("channel", {})
        
        # Handle recipient data
        recipient_data = data.get("recipient", {})
        
        return cls(
            reference=data.get("reference", ""),
            status=data.get("status", "pending"),
            amount=PayoutAmount(
                value=amount_data.get("value", 0),
                currency=amount_data.get("currency", "TZS")
            ),
            fees=PayoutAmount(
                value=fees_data.get("value", 0),
                currency=fees_data.get("currency", "TZS")
            ),
            total=PayoutAmount(
                value=total_data.get("value", 0),
                currency=total_data.get("currency", "TZS")
            ),
            channel=PayoutChannel(
                type=channel_data.get("type", ""),
                provider=channel_data.get("provider", "")
            ),
            recipient=PayoutRecipient(
                name=recipient_data.get("name", ""),
                phone=recipient_data.get("phone"),
                bank=recipient_data.get("bank"),
                account=recipient_data.get("account")
            ),
            narration=data.get("narration"),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
            external_reference=data.get("external_reference"),
            id=data.get("id"),
            metadata=data.get("metadata"),
            source=data.get("source"),
            failure_reason=data.get("failure_reason")
        )


@dataclass
class PayoutList:
    """Paginated list of payouts.
    
    Args:
        items: List of Payout objects
        total: Total number of payouts
        limit: Results per page requested
        offset: Pagination offset used
    
    Example:
        >>> result = client.list_payouts(limit=10, offset=0)
        >>> print(f"Total payouts: {result.total}")
        >>> print(f"Showing {len(result.items)} payouts")
    """
    items: list[Payout]
    total: int
    limit: int
    offset: int

    @classmethod
    def from_dict(cls, data: dict) -> "PayoutList":
        """Create PayoutList from API response dict."""
        items_data = data.get("items", [])
        return cls(
            items=[Payout.from_dict(item) for item in items_data],
            total=data.get("total", 0),
            limit=data.get("limit", 20),
            offset=data.get("offset", 0)
        )


@dataclass
class PayoutFee:
    """Payout fee calculation response.
    
    Args:
        amount: Original payout amount
        fee_amount: Fee amount
        total_amount: Total to deduct (amount + fee)
        currency: Currency code
    
    Example:
        >>> fee = client.calculate_payout_fee(amount=5000)
        >>> print(f"Fee: {fee.fee_amount} {fee.currency}")
        >>> print(f"Total: {fee.total_amount} {fee.currency}")
    """
    amount: int
    fee_amount: int
    total_amount: int
    currency: Currency

    @classmethod
    def from_dict(cls, data: dict) -> "PayoutFee":
        """Create PayoutFee from API response dict."""
        return cls(
            amount=data.get("amount", 0),
            fee_amount=data.get("fee_amount", 0),
            total_amount=data.get("total_amount", 0),
            currency=data.get("currency", "TZS")
        )