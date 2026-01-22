import asyncio
import aiohttp
import time
import sys
import json

# Configuration
BASE_URL = "http://127.0.0.1:8003" # Testing Direct Backend
API_KEY = "sk-ps-oIDkjJrueZB8lRTwgNugQw"
ENDPOINT_AUTH = "/api/v1/auth/me"
ENDPOINT_COMPRESS = "/api/v1/compress"

# Load Test Params
CONCURRENT_REQUESTS = 50
TOTAL_REQUESTS = 1000

async def verify_key(session):
    print(f"[*] Verifying API Key: {API_KEY[:8]}...")
    try:
        async with session.get(f"{BASE_URL}{ENDPOINT_AUTH}", headers={"X-API-Key": API_KEY}) as resp:
            if resp.status == 200:
                user = await resp.json()
                print(f"[+] Key is VALID. User: {user.get('email')} | Tier: {user.get('tier')} | Usage: {user.get('usage_count')}/{user.get('max_usage')}")
                return True
            else:
                text = await resp.text()
                print(f"[-] Key Verification FAILED: {resp.status} - {text}")
                return False
    except Exception as e:
        print(f"[!] Connection Error: {e}")
        return False

async def send_request(session, req_id):
    url = f"{BASE_URL}{ENDPOINT_COMPRESS}"
    payload = {
        "text": f"Optimize this text request number {req_id}",
        "model": "gpt-3.5-turbo",
        "language": "en",
        "format": "text"
    }
    start = time.time()
    try:
        async with session.post(url, json=payload, headers={"X-API-Key": API_KEY}) as resp:
            latency = (time.time() - start) * 1000
            status = resp.status
            # Read body to consume stream but don't parse unless needed
            await resp.read()
            return status, latency
    except Exception as e:
        return 999, 0

async def load_test():
    print(f"\n[*] Starting Load Test on {ENDPOINT_COMPRESS}")
    print(f"[*] Target: {BASE_URL}")
    print(f"[*] Requests: {TOTAL_REQUESTS} | Concurrency: {CONCURRENT_REQUESTS}")
    
    async with aiohttp.ClientSession() as session:
        # 1. Verify Key
        if not await verify_key(session):
            print("[!] Aborting Load Test due to invalid key.")
            return

        # 2. Run Load Test
        print("\n[*] Sending requests...")
        tasks = []
        results = []
        
        start_time = time.time()
        
        # Batching tasks to respect concurrency
        # for i in range(TOTAL_REQUESTS):
        #    tasks.append(send_request(session, i))
            
        # Run all
        # Note: This runs ALL at once if we just use gather. 
        # To limit concurrency properly we'd use a semaphore, but for "pressure" testing, 
        # dumping them all on the event loop is a good stress test.
        # But let's use a semaphore to be realistic about client capability vs server.
        
        sem = asyncio.Semaphore(CONCURRENT_REQUESTS)
        
        async def bounded_send(req_id):
            async with sem:
                return await send_request(session, req_id)
        
        bounded_tasks = [bounded_send(i) for i in range(TOTAL_REQUESTS)]
        results = await asyncio.gather(*bounded_tasks)
        
        duration = time.time() - start_time
        
        # 3. Analyze
        status_counts = {}
        latencies = []
        
        for status, latency in results:
            status_counts[status] = status_counts.get(status, 0) + 1
            if status == 200:
                latencies.append(latency)
                
        print("\n" + "="*40)
        print("LOAD TEST RESULTS")
        print("="*40)
        print(f"Total Time: {duration:.2f}s")
        print(f"Throughput: {TOTAL_REQUESTS / duration:.2f} req/sec")
        print("-" * 20)
        print("Status Codes:")
        for code, count in status_counts.items():
            desc = ""
            if code == 200: desc = "(Success)"
            elif code == 429: desc = "(Rate Limited)"
            elif code == 500: desc = "(Server Error)"
            elif code == 999: desc = "(Client Error)"
            print(f"  {code}: {count} {desc}")
        print("-" * 20)
        if latencies:
            avg_lat = sum(latencies) / len(latencies)
            max_lat = max(latencies)
            min_lat = min(latencies)
            print(f"Latency (200 OK):")
            print(f"  Avg: {avg_lat:.2f}ms")
            print(f"  Min: {min_lat:.2f}ms")
            print(f"  Max: {max_lat:.2f}ms")
        else:
            print("No successful requests to measure latency.")
            
        if status_counts.get(429, 0) > 0:
            print("\n[!] Rate Limiting Triggered! System is protecting itself.")
            
        print("="*40)

if __name__ == "__main__":
    # Check if aiohttp is installed
    try:
        import aiohttp
    except ImportError:
        print("Installing aiohttp...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
        
    asyncio.run(load_test())
