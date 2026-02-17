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


PayoutChannel = Literal["mobile", "bank"]
PayoutStatus = Literal["pending", "completed", "failed", "reversed"]
PayoutProvider = Literal[
    "airtel", "tigo", "halopesa",  # mobile money providers
    "bank"  # bank transfers
]
BankCode = Literal[
    "ABSA", "ACCESS", "AKIBA", "AMANA", "AZANIA", "BANCABC", "BARODA", 
    "BOA", "BOI", "CANARA", "CITI", "CRDB", "DASHENG", "DCB", "DTB", 
    "ECOBANK", "EQUITY", "EXIM", "FNB", "GT BANK", "HABIB", "ICB", 
    "IMBANK", "KCB", "KILIMANJARO", "MAENDELEO", "MKOMBOZI", "MWALIMU", 
    "MWANGA", "NBC", "NCBA", "NMB", "PBZ", "SCB", "SELCOMPESA", 
    "STANBIC", "TCB", "UBA", "UCHUMI", "YETU"
]
PayoutEvent = Literal[
    "payout.completed",
    "payout.failed"
]
