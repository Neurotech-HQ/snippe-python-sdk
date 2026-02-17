#!/usr/bin/env python
"""
Test script for Snippe SDK payout functionality.
Run with: python test_payout.py
"""

import os
import json
import time
from snippe import Snippe
from snippe.exceptions import SnippeError

# Hardcoded API key for testing
API_KEY = "snp_YOUR_API_KEY_HERE"

def test_mobile_payout():
    """Test creating a mobile money payout."""
    
    client = Snippe(API_KEY)
    
    try:
        print("=" * 50)
        print("Testing Mobile Money Payout")
        print("=" * 50)
        
        # Check balance first
        print("\n1. Checking current balance...")
        balance = client.get_balance()
        print(f"   Available: {balance.available_balance} {balance.currency}")
        print(f"   Total: {balance.balance} {balance.currency}")
        
        # Check if sufficient balance
        amount = 1000
        print(f"\n2. Checking fee for {amount} TZS...")
        fee_info = client.calculate_payout_fee(amount)
        print(f"   Fee: {fee_info.fee_amount} {fee_info.currency}")
        print(f"   Total needed: {fee_info.total_amount} {fee_info.currency}")
        
        if balance.available_balance < fee_info.total_amount:
            print(f"\n⚠️  Insufficient balance! Need {fee_info.total_amount} but have {balance.available_balance}")
            return None
        
        # Create mobile payout
        print("\n3. Creating mobile payout...")
        payout = client.create_mobile_payout(
            amount=amount,
            recipient_name="Jackson Mushi",
            recipient_phone="255755660639",
            narration="Test payout from SDK",
            metadata={
                "test_id": "payout-001",
                "environment": "development"
            },
            idempotency_key=f"test-payout-{int(time.time())}"  # Unique timestamp-based key
        )
        
        print(f"\n✅ Payout created successfully!")
        print(f"   Reference: {payout.reference}")
        print(f"   Status: {payout.status}")
        print(f"   Amount: {payout.amount.value} {payout.amount.currency}")
        print(f"   Fee: {payout.fees.value} {payout.fees.currency}")
        print(f"   Total deducted: {payout.total.value} {payout.total.currency}")
        print(f"   Channel: {payout.channel.provider}")
        print(f"   Recipient: {payout.recipient.name} ({payout.recipient.phone})")
        
        if payout.narration:
            print(f"   Narration: {payout.narration}")
        
        print("\n4. Getting payout status...")
        time.sleep(2)
        
        status = client.get_payout(payout.reference)
        print(f"   Status: {status.status}")
        if status.completed_at:
            print(f"   Completed at: {status.completed_at}")
        if status.failure_reason:
            print(f"   Failure reason: {status.failure_reason}")
            
        return payout
        
    except SnippeError as e:
        print(f"\n❌ Error: {e.message}")
        print(f"   HTTP Code: {e.code}")
        print(f"   Error Code: {e.error_code}")
        return None
    finally:
        client.close()

def test_list_payouts():
    """Test listing payouts."""
    
    client = Snippe(API_KEY)
    
    try:
        print("\n" + "=" * 50)
        print("Testing List Payouts")
        print("=" * 50)
        
        result = client.list_payouts(limit=5, offset=0)
        
        print(f"\nTotal payouts: {result.total}")
        print(f"Showing: {len(result.items)} payouts")
        print()
        
        for i, payout in enumerate(result.items, 1):
            print(f"{i}. Reference: {payout.reference}")
            print(f"   Status: {payout.status}")
            print(f"   Amount: {payout.amount.value} {payout.amount.currency}")
            print(f"   Recipient: {payout.recipient.name}")
            print(f"   Created: {payout.created_at}")
            print()
            
    except SnippeError as e:
        print(f"\n❌ Error: {e.message}")
    finally:
        client.close()

def test_payout_fee():
    """Test calculating payout fee."""
    
    client = Snippe(API_KEY)
    
    try:
        print("\n" + "=" * 50)
        print("Testing Calculate Payout Fee")
        print("=" * 50)
        
        amount = 5000
        fee_info = client.calculate_payout_fee(amount)
        
        print(f"\n✅ Fee calculated successfully!")
        print(f"Amount: {fee_info.amount} {fee_info.currency}")
        print(f"Fee: {fee_info.fee_amount} {fee_info.currency}")
        print(f"Total: {fee_info.total_amount} {fee_info.currency}")
        
    except SnippeError as e:
        print(f"\n❌ Error: {e.message}")
    finally:
        client.close()


def test_bank_payout():
    """Test creating a bank transfer payout."""
    
    client = Snippe(API_KEY)
    
    try:
        print("\n" + "=" * 50)
        print("Testing Bank Transfer Payout")
        print("=" * 50)
        
        # Check balance first
        print("\n1. Checking current balance...")
        balance = client.get_balance()
        print(f"   Available: {balance.available_balance} {balance.currency}")
        print(f"   Total: {balance.balance} {balance.currency}")
        
        # Test with a small amount
        amount = 2000
        print(f"\n2. Checking fee for {amount} TZS...")
        fee_info = client.calculate_payout_fee(amount)
        print(f"   Fee: {fee_info.fee_amount} {fee_info.currency}")
        print(f"   Total needed: {fee_info.total_amount} {fee_info.currency}")
        
        if balance.available_balance < fee_info.total_amount:
            print(f"\n⚠️  Insufficient balance! Need {fee_info.total_amount} but have {balance.available_balance}")
            return None
        
        # Create bank payout
        print("\n3. Creating bank transfer payout...")
        payout = client.create_bank_payout(
            amount=amount,
            recipient_name="Jackson Mushi",
            recipient_bank="SELCOMPESA",  # Using CRDB as example
            recipient_account="0755660639",  # Example account number
            narration="Test bank transfer from SDK",
            metadata={
                "test_id": "bank-payout-001",
                "environment": "development"
            },
            idempotency_key=f"test-bank-{int(time.time())}"
        )
        
        print(f"\n✅ Bank payout created successfully!")
        print(f"   Reference: {payout.reference}")
        print(f"   Status: {payout.status}")
        print(f"   Amount: {payout.amount.value} {payout.amount.currency}")
        print(f"   Fee: {payout.fees.value} {payout.fees.currency}")
        print(f"   Total deducted: {payout.total.value} {payout.total.currency}")
        print(f"   Channel: {payout.channel.type} ({payout.channel.provider})")
        print(f"   Recipient: {payout.recipient.name}")
        print(f"   Bank: {payout.recipient.bank}")
        print(f"   Account: {payout.recipient.account}")
        
        if payout.narration:
            print(f"   Narration: {payout.narration}")
        
        print("\n4. Getting payout status...")
        time.sleep(2)
        
        status = client.get_payout(payout.reference)
        print(f"   Status: {status.status}")
        if status.completed_at:
            print(f"   Completed at: {status.completed_at}")
        if status.failure_reason:
            print(f"   Failure reason: {status.failure_reason}")
            
        return payout
        
    except SnippeError as e:
        print(f"\n❌ Error: {e.message}")
        print(f"   HTTP Code: {e.code}")
        print(f"   Error Code: {e.error_code}")
        return None
    finally:
        client.close()

if __name__ == "__main__":
    print("🔧 SNIPPE SDK PAYOUT TEST")
    print("=" * 50)
    print(f"Using API key: {API_KEY[:10]}...{API_KEY[-10:]}")
    print()
    
    # Run tests
    test_payout_fee()
    test_list_payouts()
    payout = test_mobile_payout()
    
    if payout:
        print("\n✅ Mobile payout test passed!")
    else:
        print("\n❌ Mobile payout test failed or skipped due to insufficient balance")

    # Test bank payout (if balance available)
    bank_payout = test_bank_payout()
    if bank_payout:
        print("\n✅ Bank payout test passed!")
    else:
        print("\n⚠️  Bank payout test skipped (insufficient balance)")
    
    print("\n" + "=" * 50)
    print("Tests completed!")