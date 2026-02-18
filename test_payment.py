#!/usr/bin/env python
"""
Test script for Snippe SDK payment functionality.
Run with: python test_payment.py
"""

import base64
import time
import os
import webbrowser
from PIL import Image
import io

from snippe import Customer, Snippe
from snippe.exceptions import SnippeError

# Hardcoded API key for testing
API_KEY = "snp_YOUR_API_KEY_HERE"

def open_image(filename):
    """Open image with default viewer."""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(filename)
        elif os.name == 'posix':  # macOS and Linux
            if 'darwin' in os.sys.platform:  # macOS
                os.system(f'open "{filename}"')
            else:  # Linux
                os.system(f'xdg-open "{filename}"')
        return True
    except Exception as e:
        print(f"   Could not open image: {e}")
        return False

def save_qr_code(qr_base64, filename):
    """
    Save base64 QR code to image file.
    
    Args:
        qr_base64: Base64 string of QR code
        filename: Output filename
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Clean the base64 string
        qr_base64 = qr_base64.strip()
        
        # Calculate and add proper padding
        padding_needed = (4 - len(qr_base64) % 4) % 4
        if padding_needed:
            qr_base64 += "=" * padding_needed
            print(f"   Added {padding_needed} padding characters")
        
        print(f"   Base64 length: {len(qr_base64)}")
        
        # Decode
        qr_bytes = base64.b64decode(qr_base64)
        
        # Save as PNG
        with open(filename, "wb") as f:
            f.write(qr_bytes)
        
        # Verify it's a valid image
        img = Image.open(io.BytesIO(qr_bytes))
        print(f"   ✅ QR code saved as {filename}")
        print(f"   Image size: {img.size}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error saving QR code: {e}")
        return False

def test_mobile_payment():
    """Test creating a mobile money payment."""
    
    client = Snippe(API_KEY)
    
    try:
        print("=" * 50)
        print("Testing Mobile Money Payment")
        print("=" * 50)
        
        # Check balance first
        print("\n1. Checking current balance...")
        balance = client.get_balance()
        print(f"   Available: {balance.available_balance} {balance.currency}")
        print(f"   Total: {balance.balance} {balance.currency}")
        
        # Create mobile payment
        amount = 1000
        print(f"\n2. Creating mobile payment of {amount} TZS...")
        
        payment = client.create_mobile_payment(
            amount=amount,
            currency="TZS",
            phone_number="0712345678",
            customer=Customer(
                firstname="John",
                lastname="Doe",
                email="john@example.com",
                phone="0712345678"
            ),
            webhook_url="https://webhook.site/test",  # Optional test webhook
            metadata={
                "test_id": f"payment-{int(time.time())}",
                "environment": "development"
            },
            idempotency_key=f"test-payment-{int(time.time())}"
        )
        
        print(f"\n✅ Payment created successfully!")
        print(f"   Reference: {payment.reference}")
        print(f"   Status: {payment.status}")
        print(f"   Amount: {payment.amount} {payment.currency}")
        print(f"   Type: {payment.payment_type}")
        
        if payment.expires_at:
            print(f"   Expires at: {payment.expires_at}")
        
        print("\n3. Getting payment status...")
        time.sleep(2)
        
        status = client.get_payment(payment.reference)
        print(f"   Status: {status.status}")
        
        return payment
        
    except SnippeError as e:
        print(f"\n❌ Error: {e.message}")
        print(f"   HTTP Code: {e.code}")
        print(f"   Error Code: {e.error_code}")
        return None
    finally:
        client.close()

def test_card_payment():
    """Test creating a card payment."""
    
    client = Snippe(API_KEY)
    
    try:
        print("\n" + "=" * 50)
        print("Testing Card Payment")
        print("=" * 50)
        
        amount = 5000
        print(f"\nCreating card payment of {amount} TZS...")
        
        payment = client.create_card_payment(
            amount=amount,
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
            callback_url="https://yourapp.com/callback",  # Required for card
            webhook_url="https://webhook.site/test",
            metadata={"order_id": "ORD-123"},
            idempotency_key=f"test-card-{int(time.time())}"
        )
        
        print(f"\n✅ Card payment created successfully!")
        print(f"   Reference: {payment.reference}")
        print(f"   Status: {payment.status}")
        print(f"   Payment URL: {payment.payment_url}")
        print(f"   Amount: {payment.amount} {payment.currency}")
        
        # Ask if user wants to open the payment URL
        response = input("\n🌐 Open payment URL in browser? (y/n): ")
        if response.lower() == 'y':
            webbrowser.open(payment.payment_url)
            print("   ✅ Browser opened")
        
        return payment
        
    except SnippeError as e:
        print(f"\n❌ Error: {e.message}")
        return None
    finally:
        client.close()

def test_qr_payment():
    """Test creating a QR code payment."""
    
    client = Snippe(API_KEY)
    
    try:
        print("\n" + "=" * 50)
        print("Testing QR Code Payment")
        print("=" * 50)
        
        amount = 2500
        print(f"\nCreating QR payment of {amount} TZS...")
        
        payment = client.create_qr_payment(
            amount=amount,
            currency="TZS",
            phone_number="0712345678",
            customer=Customer(
                firstname="John",
                lastname="Doe",
                email="john@example.com"
            ),
            webhook_url="https://webhook.site/test",
            metadata={"table": "5", "restaurant": "Test Cafe"},
            idempotency_key=f"test-qr-{int(time.time())}"
        )
        
        print(f"\n✅ QR payment created successfully!")
        print(f"   Reference: {payment.reference}")
        print(f"   Status: {payment.status}")
        print(f"   Amount: {payment.amount} {payment.currency}")
        print(f"   Payment Token: {payment.payment_token}")
        
        if payment.payment_qr_code:
            # This is raw QR data, not base64
            qr_data = payment.payment_qr_code
            print(f"\n📊 QR Data Length: {len(qr_data)}")
            print(f"📊 QR Data Preview: {qr_data[:50]}...")
            
            # Generate QR code image from the data
            try:
                import qrcode
                filename = f"qr_{payment.reference[:8]}.png"
                
                # Create QR code
                qr = qrcode.QRCode(
                    version=1,
                    box_size=10,
                    border=4
                )
                qr.add_data(qr_data)
                qr.make(fit=True)
                
                # Create image
                img = qr.make_image(fill_color="black", back_color="white")
                img.save(filename)
                print(f"\n✅ QR code image generated and saved as {filename}")
                
                # Ask if user wants to open it
                response = input("\n📱 Open QR code image? (y/n): ")
                if response.lower() == 'y':
                    open_image(filename)
                    
            except ImportError:
                print("\n⚠️  Install qrcode to generate images: pip install qrcode[pil]")
                # Save raw data to file as fallback
                with open(f"qr_data_{payment.reference[:8]}.txt", "w") as f:
                    f.write(qr_data)
                print(f"✅ Raw QR data saved to qr_data_{payment.reference[:8]}.txt")
        
        return payment
        
    except SnippeError as e:
        print(f"\n❌ Error: {e.message}")
        print(f"   HTTP Code: {e.code}")
        print(f"   Error Code: {e.error_code}")
        return None
    finally:
        client.close()

def test_list_payments():
    """Test listing payments."""
    
    client = Snippe(API_KEY)
    
    try:
        print("\n" + "=" * 50)
        print("Testing List Payments")
        print("=" * 50)
        
        result = client.list_payments(limit=5, offset=0)
        
        print(f"\nTotal payments: {len(result.payments)}")
        print(f"Showing: {len(result.payments)} payments")
        print()
        
        for i, payment in enumerate(result.payments, 1):
            print(f"{i}. Reference: {payment.reference}")
            print(f"   Status: {payment.status}")
            print(f"   Amount: {payment.amount} {payment.currency}")
            print(f"   Type: {payment.payment_type}")
            print(f"   Created: {payment.created_at}")
            print()
            
    except SnippeError as e:
        print(f"\n❌ Error: {e.message}")
    finally:
        client.close()

if __name__ == "__main__":
    print("🔧 SNIPPE SDK PAYMENT TEST")
    print("=" * 50)
    print(f"Using API key: {API_KEY[:10]}...{API_KEY[-10:]}")
    print()
    
    # Run tests
    test_list_payments()
    test_mobile_payment()
    test_card_payment()
    test_qr_payment()
    
    print("\n" + "=" * 50)
    print("Tests completed!")