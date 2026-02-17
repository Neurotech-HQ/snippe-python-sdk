"""Snippe Payment API client."""

import uuid
from typing import Any, Optional

import httpx

from .exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    SnippeError,
    ValidationError,
)
from .models import (
    Balance, 
    Customer, 
    Payment, 
    PaymentDetails, 
    PaymentList,    
    Payout,
    PayoutList,
    PayoutFee,
    PayoutRecipient
    )
from .types import (
    Currency, 
    PaymentType,
    PayoutChannel as PayoutChannelType,
    BankCode
    )


class Snippe:
    """
    Snippe Payment API client.

    Usage:
        >>> from snippe import Snippe, Customer
        >>> client = Snippe("your_api_key")
        >>> payment = client.create_mobile_payment(
        ...     amount=1000,
        ...     currency="TZS",
        ...     phone_number="0712345678",
        ...     customer=Customer(firstname="John", lastname="Doe")
        ... )

    Args:
        api_key: Your Snippe API key
        base_url: Override the base URL (optional, defaults to https://api.snippe.sh/api/v1)
        timeout: Request timeout in seconds (default: 30.0)
    
    Example with context manager:
        >>> with Snippe("your_api_key") as client:
        ...     payment = client.create_mobile_payment(...)

    """

    BASE_URL = "https://api.snippe.sh/api/v1"

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize Snippe client.

        Args:
            api_key: Your Snippe API key
            base_url: Override the base URL (for testing)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and raise appropriate exceptions."""
        try:
            data = response.json()
        except Exception:
            data = {"message": response.text}

        if response.status_code == 200 or response.status_code == 201:
            return data.get("data", data)

        message = data.get("message", "Unknown error")
        error_code = data.get("error_code", "")
        code = response.status_code

        if code == 401:
            raise AuthenticationError(message, code, error_code)
        elif code == 400:
            raise ValidationError(message, code, error_code)
        elif code == 404:
            raise NotFoundError(message, code, error_code)
        elif code == 429:
            raise RateLimitError(message, code, error_code)
        elif code >= 500:
            raise ServerError(message, code, error_code)
        else:
            raise SnippeError(message, code, error_code)

    def _create_payment(
        self,
        payment_type: PaymentType,
        amount: int,
        currency: Currency,
        phone_number: str,
        customer: Customer,
        callback_url: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[dict] = None,
        idempotency_key: Optional[str] = None,
    ) -> Payment:
        """Internal method to create a payment."""
        payload = {
            "payment_type": payment_type,
            "details": PaymentDetails(amount, currency, callback_url).to_dict(),
            "phone_number": phone_number,
            "customer": customer.to_dict(),
        }
        if webhook_url:
            payload["webhook_url"] = webhook_url
        if metadata:
            payload["metadata"] = metadata

        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        response = self._client.post("/payments", json=payload, headers=headers)
        data = self._handle_response(response)
        return Payment.from_dict(data)

    def create_mobile_payment(
        self,
        amount: int,
        currency: Currency,
        phone_number: str,
        customer: Customer,
        callback_url: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[dict] = None,
        idempotency_key: Optional[str] = None,
    ) -> Payment:
        """
        Create a mobile money payment (USSD push).

        Customer receives a USSD prompt to confirm payment.

        Args:
            amount: Amount in smallest currency unit (e.g., cents)
            currency: Currency code (TZS, KES, UGX)
            phone_number: Customer phone number
            customer: Customer information
            callback_url: URL to redirect after payment
            webhook_url: URL to receive payment status updates
            metadata: Custom key-value pairs
            idempotency_key: Unique key to prevent duplicates

        Returns:
            Payment object with reference and status

        Example:
            >>> payment = client.create_mobile_payment(
            ...     amount=1000,
            ...     currency="TZS",
            ...     phone_number="0712345678",
            ...     customer=Customer(firstname="John", lastname="Doe")
            ... )

        """
        return self._create_payment(
            payment_type="mobile",
            amount=amount,
            currency=currency,
            phone_number=phone_number,
            customer=customer,
            callback_url=callback_url,
            webhook_url=webhook_url,
            metadata=metadata,
            idempotency_key=idempotency_key,
        )

    def create_card_payment(
        self,
        amount: int,
        currency: Currency,
        phone_number: str,
        customer: Customer,
        callback_url: str,
        webhook_url: Optional[str] = None,
        metadata: Optional[dict] = None,
        idempotency_key: Optional[str] = None,
    ) -> Payment:
        """
        Create a card payment.

        Returns a payment_url to redirect the customer.

        Args:
            amount: Amount in smallest currency unit
            currency: Currency code (TZS, KES, UGX)
            phone_number: Customer phone number
            customer: Customer information (must include address fields)
            callback_url: URL to redirect after payment (required)
            webhook_url: URL to receive payment status updates
            metadata: Custom key-value pairs
            idempotency_key: Unique key to prevent duplicates

        Returns:
            Payment object with payment_url for redirect

        Example:
            >>> payment = client.create_card_payment(
            ...     amount=50000,
            ...     currency="TZS",
            ...     phone_number="0712345678",
            ...     customer=Customer(
            ...         firstname="John",
            ...         lastname="Doe",
            ...         address="123 Main Street",
            ...         city="Dar es Salaam",
            ...         country="TZ"
            ...     ),
            ...     callback_url="https://myapp.com/callback"
            ... )
            >>> print(payment.payment_url)
        """
        return self._create_payment(
            payment_type="card",
            amount=amount,
            currency=currency,
            phone_number=phone_number,
            customer=customer,
            callback_url=callback_url,
            webhook_url=webhook_url,
            metadata=metadata,
            idempotency_key=idempotency_key,
        )

    def create_qr_payment(
        self,
        amount: int,
        currency: Currency,
        phone_number: str,
        customer: Customer,
        callback_url: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[dict] = None,
        idempotency_key: Optional[str] = None,
    ) -> Payment:
        """
        Create a dynamic QR code payment.

        Returns a QR code for the customer to scan.

        Args:
            amount: Amount in smallest currency unit
            currency: Currency code (TZS, KES, UGX)
            phone_number: Customer phone number
            customer: Customer information
            callback_url: URL to redirect after payment
            webhook_url: URL to receive payment status updates
            metadata: Custom key-value pairs
            idempotency_key: Unique key to prevent duplicates

        Returns:
            Payment object with qr_code and payment_token

        Example:
            >>> payment = client.create_qr_payment(
            ...     amount=25000,
            ...     currency="TZS",
            ...     phone_number="0712345678",
            ...     customer=Customer(firstname="John", lastname="Doe")
            ... )
            >>> # Display payment.payment_qr_code to customer
        """
        return self._create_payment(
            payment_type="dynamic-qr",
            amount=amount,
            currency=currency,
            phone_number=phone_number,
            customer=customer,
            callback_url=callback_url,
            webhook_url=webhook_url,
            metadata=metadata,
            idempotency_key=idempotency_key,
        )

    def get_payment(self, reference: str) -> Payment:
        """
        Get payment status by reference.

        Args:
            reference: Payment reference from create response

        Returns:
            Payment object with current status

        Example:
            >>> payment = client.get_payment("payment_ref_123")
            >>> print(f"Status: {payment.status}")
            >>> if payment.status == "completed":
            ...     # Fulfill order
            ...     pass
        """
        response = self._client.get(f"/payments/{reference}")
        data = self._handle_response(response)
        return Payment.from_dict(data)

    def list_payments(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> PaymentList:
        """
        List all payments for your account.

        Args:
            limit: Results per page (max 100)
            offset: Pagination offset

        Returns:
            PaymentList with payments and pagination info

        Example:
            >>> result = client.list_payments(limit=10, offset=0)
            >>> for payment in result.payments:
            ...     print(f"{payment.reference}: {payment.status}")
            >>> print(f"Total shown: {len(result.payments)}")
        """
        response = self._client.get(
            "/payments",
            params={"limit": limit, "offset": offset},
        )
        data = self._handle_response(response)
        return PaymentList.from_dict(data)

    def get_balance(self) -> Balance:
        """
        Get your current account balance.

        Returns:
            Balance object with available and pending amounts

        Example:
            >>> balance = client.get_balance()
            >>> print(f"Available: {balance.available_balance} {balance.currency}")
            >>> print(f"Total: {balance.balance} {balance.currency}")
        """
        response = self._client.get("/payments/balance")
        data = self._handle_response(response)
        return Balance.from_dict(data)

    def create_mobile_payout(
        self,
        amount: int,
        recipient_name: str,
        recipient_phone: str,
        narration: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[dict] = None,
        idempotency_key: Optional[str] = None,
        ) -> Payout:
        """
        Send money to a mobile money account.
        
        Supports Airtel Money, Mixx by Yas (Tigo), and HaloPesa.
        Funds are deducted from your available balance immediately.
        
        Args:
            amount: Amount in smallest currency unit (e.g., 5000 = 5,000 TZS)
            recipient_name: Full name of the recipient
            recipient_phone: Phone number in format 255XXXXXXXXX (e.g., 255781000000)
            narration: Description or reason for the payout (optional)
            webhook_url: URL to receive webhook notifications
            metadata: Custom key-value pairs for your reference (optional)
            idempotency_key: Unique key to prevent duplicate payouts
        
        Returns:
            Payout object with reference and status
        """
        payload = {
            "amount": amount,
            "channel": "mobile",
            "recipient_name": recipient_name,
            "recipient_phone": recipient_phone,
        }
        
        if narration:
            payload["narration"] = narration
        if webhook_url:
            payload["webhook_url"] = webhook_url
        if metadata:
            payload["metadata"] = metadata
            
        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
            
        response = self._client.post("/payouts/send", json=payload, headers=headers)
        data = self._handle_response(response)
        return Payout.from_dict(data)


    def calculate_payout_fee(self, amount: int) -> PayoutFee:
        """
        Calculate fee for a payout before sending.
        
        Always calculate fees before creating payouts to ensure you have sufficient balance.
        
        Args:
            amount: Amount in smallest currency unit to calculate fee for
            
        Returns:
            PayoutFee object with:
            - amount: Original amount
            - fee_amount: Fee amount
            - total_amount: Amount + fee
            - currency: Currency code
            
        Example:
            >>> fee = client.calculate_payout_fee(amount=5000)
            >>> print(f"Fee: {fee.fee_amount} {fee.currency}")
            >>> print(f"Total to deduct: {fee.total_amount} {fee.currency}")
        """
        response = self._client.get("/payouts/fee", params={"amount": amount})
        data = self._handle_response(response)
        return PayoutFee.from_dict(data)

    def list_payouts(
        self,
        limit: int = 20,
        offset: int = 0,
        ) -> PayoutList:
        """
        List all payouts for your account with pagination.
        
        Args:
            limit: Results per page (max 100, default: 20)
            offset: Pagination offset (default: 0)
            
        Returns:
            PayoutList object with:
            - items: List of Payout objects
            - total: Total number of payouts
            - limit: Results per page requested
            - offset: Pagination offset used
            
        Example:
            >>> result = client.list_payouts(limit=10, offset=0)
            >>> print(f"Total payouts: {result.total}")
            >>> for payout in result.items:
            ...     print(f"{payout.reference}: {payout.status}")
        """
        response = self._client.get(
            "/payouts",
            params={"limit": limit, "offset": offset},
        )
        data = self._handle_response(response)
        return PayoutList.from_dict(data)
    
    
    def get_payout(self, reference: str) -> Payout:
        """
        Get payout status by reference.
        
        Args:
            reference: Payout reference from create response
            
        Returns:
            Payout object with current status
            
        Example:
            >>> payout = client.get_payout("payout_ref_123")
            >>> print(f"Status: {payout.status}")
            >>> if payout.status == "completed":
            ...     print(f"Completed at: {payout.completed_at}")
            ... elif payout.status == "failed":
            ...     print(f"Failed: {payout.failure_reason}")
        """
        response = self._client.get(f"/payouts/{reference}")
        data = self._handle_response(response)
        return Payout.from_dict(data)



    def create_bank_payout(
        self,
        amount: int,
        recipient_name: str,
        recipient_bank: BankCode,
        recipient_account: str,
        narration: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[dict] = None,
        idempotency_key: Optional[str] = None,
    ) -> Payout:
        """
        Send money to a bank account.
        
        Supports 40+ Tanzanian banks including CRDB, NMB, NBC, ABSA.
        Funds are deducted from your available balance immediately.
        
        Args:
            amount: Amount in smallest currency unit
            recipient_name: Full name or company name
            recipient_bank: Bank code (e.g., "CRDB", "NMB", "ABSA")
            recipient_account: Bank account number
            narration: Description/reason for payout
            webhook_url: URL for webhook notifications
            metadata: Custom key-value pairs
            idempotency_key: Unique key to prevent duplicates
        
        Returns:
            Payout object with reference and status
        """
        payload = {
            "amount": amount,
            "channel": "bank",
            "recipient_name": recipient_name,
            "recipient_bank": recipient_bank,
            "recipient_account": recipient_account,
        }
        
        if narration:
            payload["narration"] = narration
        if webhook_url:
            payload["webhook_url"] = webhook_url
        if metadata:
            payload["metadata"] = metadata
            
        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
            
        response = self._client.post("/payouts/send", json=payload, headers=headers)
        data = self._handle_response(response)
        return Payout.from_dict(data)


    def close(self) -> None:
        """
        Close the HTTP client.

        Should be called when done using the client to free resources.
        Not needed when using the context manager.

        Example:
            >>> client = Snippe("api_key")
            >>> # ... do work ...
            >>> client.close()
        """
        self._client.close()

    def __enter__(self) -> "Snippe":
        return self

    def __exit__(self, *args) -> None:
        self.close()


class AsyncSnippe:
    """
    Async Snippe Payment API client.

    For use with asyncio-based frameworks like FastAPI, aiohttp, etc.

    Usage:
        >>> from snippe import AsyncSnippe, Customer
        >>> async with AsyncSnippe("your_api_key") as client:
        ...     payment = await client.create_mobile_payment(
        ...         amount=1000,
        ...         currency="TZS",
        ...         phone_number="0712345678",
        ...         customer=Customer(firstname="John", lastname="Doe")
        ...     )

    Args:
        api_key: Your Snippe API key
        base_url: Override the base URL (optional)
        timeout: Request timeout in seconds (default: 30.0)
    """


    BASE_URL = "https://api.snippe.sh/api/v1"

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """Initialize async Snippe client."""
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    async def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and raise appropriate exceptions."""
        try:
            data = response.json()
        except Exception:
            data = {"message": response.text}

        if response.status_code == 200 or response.status_code == 201:
            return data.get("data", data)

        message = data.get("message", "Unknown error")
        error_code = data.get("error_code", "")
        code = response.status_code

        if code == 401:
            raise AuthenticationError(message, code, error_code)
        elif code == 400:
            raise ValidationError(message, code, error_code)
        elif code == 404:
            raise NotFoundError(message, code, error_code)
        elif code == 429:
            raise RateLimitError(message, code, error_code)
        elif code >= 500:
            raise ServerError(message, code, error_code)
        else:
            raise SnippeError(message, code, error_code)

    async def _create_payment(
        self,
        payment_type: PaymentType,
        amount: int,
        currency: Currency,
        phone_number: str,
        customer: Customer,
        callback_url: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[dict] = None,
        idempotency_key: Optional[str] = None,
    ) -> Payment:
        """Internal method to create a payment."""
        payload = {
            "payment_type": payment_type,
            "details": PaymentDetails(amount, currency, callback_url).to_dict(),
            "phone_number": phone_number,
            "customer": customer.to_dict(),
        }
        if webhook_url:
            payload["webhook_url"] = webhook_url
        if metadata:
            payload["metadata"] = metadata

        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        response = await self._client.post("/payments", json=payload, headers=headers)
        data = await self._handle_response(response)
        return Payment.from_dict(data)

    async def create_mobile_payment(
        self,
        amount: int,
        currency: Currency,
        phone_number: str,
        customer: Customer,
        callback_url: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[dict] = None,
        idempotency_key: Optional[str] = None,
    ) -> Payment:
        """Create a mobile money payment (USSD push)."""
        return await self._create_payment(
            payment_type="mobile",
            amount=amount,
            currency=currency,
            phone_number=phone_number,
            customer=customer,
            callback_url=callback_url,
            webhook_url=webhook_url,
            metadata=metadata,
            idempotency_key=idempotency_key,
        )

    async def create_card_payment(
        self,
        amount: int,
        currency: Currency,
        phone_number: str,
        customer: Customer,
        callback_url: str,
        webhook_url: Optional[str] = None,
        metadata: Optional[dict] = None,
        idempotency_key: Optional[str] = None,
    ) -> Payment:
        """Create a card payment."""
        return await self._create_payment(
            payment_type="card",
            amount=amount,
            currency=currency,
            phone_number=phone_number,
            customer=customer,
            callback_url=callback_url,
            webhook_url=webhook_url,
            metadata=metadata,
            idempotency_key=idempotency_key,
        )

    async def create_qr_payment(
        self,
        amount: int,
        currency: Currency,
        phone_number: str,
        customer: Customer,
        callback_url: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[dict] = None,
        idempotency_key: Optional[str] = None,
    ) -> Payment:
        """Create a dynamic QR code payment."""
        return await self._create_payment(
            payment_type="dynamic-qr",
            amount=amount,
            currency=currency,
            phone_number=phone_number,
            customer=customer,
            callback_url=callback_url,
            webhook_url=webhook_url,
            metadata=metadata,
            idempotency_key=idempotency_key,
        )

    async def get_payment(self, reference: str) -> Payment:
        """Get payment status by reference."""
        response = await self._client.get(f"/payments/{reference}")
        data = await self._handle_response(response)
        return Payment.from_dict(data)

    async def list_payments(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> PaymentList:
        """List all payments for your account."""
        response = await self._client.get(
            "/payments",
            params={"limit": limit, "offset": offset},
        )
        data = await self._handle_response(response)
        return PaymentList.from_dict(data)

    async def get_balance(self) -> Balance:
        """Get your current account balance."""
        response = await self._client.get("/payments/balance")
        data = await self._handle_response(response)
        return Balance.from_dict(data)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncSnippe":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()


