import httpx
import time
import sys
import os

BASE_URL = "http://127.0.0.1:8003"
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "admin123")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("================================================================")
    print("           🛡️  PROMPTSHIELD ADMIN CONSOLE  🛡️")
    print("================================================================")

def get_pending_payments():
    try:
        resp = httpx.get(f"{BASE_URL}/api/v1/admin/payments/pending", params={"admin_secret": ADMIN_SECRET})
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            print("❌ Unauthorized. Check ADMIN_SECRET.")
            return []
        else:
            print(f"❌ Error fetching payments: {resp.text}")
            return []
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return []

def approve_payment(payment_id):
    print(f"\n⏳ Approving Payment ID: {payment_id}...")
    try:
        resp = httpx.post(f"{BASE_URL}/api/v1/admin/payments/{payment_id}/approve", params={"admin_secret": ADMIN_SECRET})
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ SUCCESS: {data['message']}")
            print(f"🔑 New User API Key: {data['new_api_key']}")
        else:
            print(f"❌ FAILED: {resp.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    input("\nPress Enter to continue...")

def main():
    while True:
        clear_screen()
        print_header()
        
        print("\n[ Fetching Pending Payments... ]")
        payments = get_pending_payments()
        
        if not payments:
            print("\n   ✨ No pending payments found. All clear!")
        else:
            print(f"\n   Found {len(payments)} pending payment(s):\n")
            print(f"   {'ID':<5} | {'User ID':<8} | {'Plan':<10} | {'Amount':<8} | {'UTR':<15} | {'Date':<20}")
            print("   " + "-"*80)
            for p in payments:
                print(f"   {p['id']:<5} | {p['user_id']:<8} | {p['plan']:<10} | ₹{p['amount']:<7} | {p['utr']:<15} | {p['created_at']}")
        
        print("\n" + "-"*80)
        print("OPTIONS:")
        print(" [ID] Enter Payment ID to Approve")
        print(" [R]  Refresh List")
        print(" [Q]  Quit")
        
        choice = input("\n> ").strip().lower()
        
        if choice == 'q':
            print("Goodbye!")
            break
        elif choice == 'r':
            continue
        elif choice.isdigit():
            approve_payment(int(choice))
        else:
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
