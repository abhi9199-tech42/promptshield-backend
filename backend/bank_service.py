from datetime import datetime, timedelta
import random

class MockBankService:
    """
    Simulates a Banking/UPI Provider API for verifying transactions.
    In a real application, this would make HTTP requests to Razorpay, Stripe, or a Bank API.
    """
    
    @staticmethod
    def verify_transaction(utr: str, expected_amount: float):
        """
        Verifies a transaction by UTR.
        
        Simulation Rules:
        - UTR starting with '000': Transaction Not Found / Invalid.
        - UTR starting with '999': Transaction Time > 10 mins ago (Expired/Old).
        - UTR starting with '888': Amount Mismatch.
        - Any other 12-digit UTR: Success (Recent & Correct Amount).
        
        Returns:
            dict: Transaction details or None if invalid.
        """
        # Basic format check
        if not utr.isdigit() or len(utr) != 12:
            return None

        # Simulate API Latency
        # time.sleep(0.5) 
        
        now = datetime.utcnow()
        
        # Scenario 1: Invalid/Not Found
        if utr.startswith('000'):
            return None
            
        # Scenario 2: Old Transaction (e.g., paid 30 mins ago)
        if utr.startswith('999'):
            return {
                "utr": utr,
                "amount": expected_amount,
                "timestamp": now - timedelta(minutes=30),
                "status": "SUCCESS",
                "sender": "Simulated User",
                "receiver": "PromptShield Inc"
            }

        # Scenario 3: Amount Mismatch (e.g., user paid ₹1 instead of ₹99)
        if utr.startswith('888'):
             return {
                "utr": utr,
                "amount": 1.00, # Wrong amount
                "timestamp": now - timedelta(minutes=2),
                "status": "SUCCESS",
                "sender": "Simulated User",
                "receiver": "PromptShield Inc"
            }

        # Scenario 4: Success (Happy Path)
        return {
            "utr": utr,
            "amount": expected_amount,
            "timestamp": now - timedelta(minutes=1), # Paid 1 minute ago
            "status": "SUCCESS",
            "sender": "Simulated User",
            "receiver": "PromptShield Inc"
        }
