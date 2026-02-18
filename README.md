# Snippe Python SDK

[![PyPI version](https://img.shields.io/pypi/v/snippe)](https://pypi.org/project/snippe/)
[![PyPI downloads](https://img.shields.io/pypi/dm/snippe)](https://pypi.org/project/snippe/)
[![Python versions](https://img.shields.io/pypi/pyversions/snippe)](https://pypi.org/project/snippe/)
[![License](https://img.shields.io/pypi/l/snippe)](https://pypi.org/project/snippe/)

Official Python SDK for [Snippe Payment API](https://snippe.sh) - Accept payments via mobile money, card, and QR code in East Africa.

## Installation

```bash
pip install snippe
```

## Quick Start

```python
from snippe import Snippe, Customer

client = Snippe("your_api_key")

# Create a mobile money payment
payment = client.create_mobile_payment(
    amount=1000,
    currency="TZS",
    phone_number="0788500000",
    customer=Customer(firstname="John", lastname="Doe"),
)

print(f"Payment reference: {payment.reference}")
print(f"Status: {payment.status}")
```

## Payment Types

### Mobile Money (USSD Push)

Customer receives a USSD prompt on their phone to confirm payment.

```python
payment = client.create_mobile_payment(
    amount=5000,
    currency="TZS",
    phone_number="0712345678",
    customer=Customer(
        firstname="Jane",
        lastname="Doe",
        email="jane@example.com"  # optional
    ),
    webhook_url="https://yourapp.com/webhooks",  # optional
    metadata={"order_id": "ORD-123"},  # optional
)
```

### Card Payment

Returns a `payment_url` to redirect the customer to complete payment.

```python
payment = client.create_card_payment(
    amount=50000,
    currency="TZS",
    phone_number="0712345678",
    customer=Customer(
        firstname="John",
        lastname="Doe",
        email="john@example.com",
        address="123 Main Street",
        city="Dar es Salaam",
        state="DSM",
        postcode="14101",
        country="TZ",
    ),
    callback_url="https://yourapp.com/callback",  # required for card
    webhook_url="https://yourapp.com/webhooks",
)

# Redirect customer to this URL
print(payment.payment_url)
```

### QR Code Payment

Returns a QR code for the customer to scan.

```python
payment = client.create_qr_payment(
    amount=25000,
    currency="TZS",
    phone_number="0712345678",
    customer=Customer(firstname="John", lastname="Doe"),
)

# Display this QR code to customer
print(payment.payment_qr_code)
print(payment.payment_token)
```

## Check Payment Status

```python
payment = client.get_payment("payment_reference")
print(f"Status: {payment.status}")  # pending, completed, failed, expired, voided
```

## List Payments

```python
result = client.list_payments(limit=20, offset=0)
for payment in result.payments:
    print(f"{payment.reference}: {payment.status}")
```

## Check Balance

```python
balance = client.get_balance()
print(f"Available: {balance.available_balance} {balance.currency}")
```

## Disbursements (Payouts)

Send money to mobile money accounts and bank accounts.

## Mobile Money Payouts

Send money to Airtel Money, Mixx by Yas (Tigo), and HaloPesa.

Calculate fee first (recommended)

```python
fee = client.calculate_payout_fee(amount=5000)
print(f"Fee: {fee.fee_amount} {fee.currency}")
print(f"Total to deduct: {fee.total_amount} {fee.currency}")
```

Create mobile money payout

```python
payout = client.create_mobile_payout(
    amount=5000,
    recipient_name="John Doe",
    recipient_phone="255781000000",  # Format: 255XXXXXXXXX
    narration="Salary payment January 2026",
    webhook_url="https://yourapp.com/webhooks",
    metadata={"employee_id": "EMP-001"},
    idempotency_key="unique_id_123"  # Prevent duplicates
)

print(f"Payout reference: {payout.reference}")
print(f"Status: {payout.status}")
print(f"Amount: {payout.amount.value} {payout.amount.currency}")
print(f"Fee: {payout.fees.value} {payout.fees.currency}")
```

## Bank Transfer Payouts

Send money to 40+ Tanzanian banks including CRDB, NMB, NBC, and ABSA.

```python
payout = client.create_bank_payout(
    amount=50000,
    recipient_name="John Doe",
    recipient_bank="CRDB",  # Bank code from supported banks list
    recipient_account="0211049375",
    narration="Invoice payment INV-2026-001",
    webhook_url="https://yourapp.com/webhooks",
    metadata={"invoice_id": "INV-2026-001"},
)

print(f"Reference: {payout.reference}")
print(f"Status: {payout.status}")
```

List Payouts

```python
result = client.list_payouts(limit=10, offset=0)
print(f"Total payouts: {result.total}")
for payout in result.items:
    print(f"{payout.reference}: {payout.status} - {payout.amount.value} {payout.amount.currency}")
Get Payout Status
python
payout = client.get_payout("payout_reference")
print(f"Status: {payout.status}")
if payout.status == "failed":
    print(f"Reason: {payout.failure_reason}")
```

Get Payout Status

```python
payout = client.get_payout("payout_reference")
print(f"Status: {payout.status}")
if payout.status == "failed":
    print(f"Reason: {payout.failure_reason}")
```


## Payout Statu
| Status        | Description                                   |
|---------------|-----------------------------------------------|
| `pending`     | Payout created, awaiting processing           |
| `completed`   | Payout successful, recipient received funds   |
| `failed`      | Payout failed (check failure_reason)          |
| `reversed`    | Payout was reversed after completion          |


## Webhooks

Verify and parse webhook events from Snippe.

```python
from snippe import verify_webhook, WebhookVerificationError

# In your webhook endpoint
try:
    payload = verify_webhook(
        body=request.body.decode(),
        signature=request.headers["X-Webhook-Signature"],
        timestamp=request.headers["X-Webhook-Timestamp"],
        signing_key="your_webhook_signing_key",
    )

    if payload.event == "payment.completed":
        print(f"Payment {payload.reference} completed!")
        # Fulfill the order
    elif payload.event == "payment.failed":
        print(f"Payment {payload.reference} failed")
        # Notify customer
    elif payload.event == "payout.completed":
        print(f"Payout {payload.reference} completed!")
    elif payload.event == "payout.failed":
        print(f"Payout {payload.reference} failed")

except WebhookVerificationError as e:
    print(f"Invalid webhook: {e}")
```

### Webhook Events

| Event | Description |
|-------|-------------|
| `payment.completed` | Payment successful |
| `payment.failed` | Payment declined or failed |
| `payment.expired` | Payment timed out |
| `payment.voided` | Payment cancelled |

## Async Support

For async applications (FastAPI, aiohttp, etc.):

```python
from snippe import AsyncSnippe, Customer

async def create_payment():
    async with AsyncSnippe("your_api_key") as client:
        payment = await client.create_mobile_payment(
            amount=1000,
            currency="TZS",
            phone_number="0788500000",
            customer=Customer(firstname="John", lastname="Doe"),
        )
        return payment
```

## Idempotency

Prevent duplicate payments by providing an idempotency key:

```python
payment = client.create_mobile_payment(
    amount=1000,
    currency="TZS",
    phone_number="0788500000",
    customer=Customer(firstname="John", lastname="Doe"),
    idempotency_key="unique_order_id_123",  # Your unique identifier
)
```

## Error Handling

```python
from snippe import (
    Snippe,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ForbiddenError,
    ConflictError,
    UnprocessableEntityError,
    RateLimitError,
    ServerError,
)

try:
    payment = client.create_mobile_payment(...)
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except NotFoundError:
    print("Payment not found")
except ForbiddenError:
    print("Not authorized for this operation")
except ConflictError:
    print("Resource already exists")
except UnprocessableEntityError:
    print("Idempotency key mismatch")
except RateLimitError:
    print("Too many requests, slow down")
except ServerError:
    print("Snippe server error, try again later")
```

## Supported Currencies

| Currency | Country |
|----------|---------|
| TZS | Tanzania |
| KES | Kenya |
| UGX | Uganda |

## License

MIT
