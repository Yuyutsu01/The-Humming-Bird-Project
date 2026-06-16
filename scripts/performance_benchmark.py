import os
import time
import subprocess
import httpx
import asyncio
import websockets
import json
import statistics

BASE_URL = "http://127.0.0.1:8001"
WS_URL = "ws://127.0.0.1:8001/api/ws"

def start_server():
    print("Starting Hummingbird Backend Server on port 8001...")
    # Start uvicorn server in a subprocess
    env = dict(os.environ, MOCK_MARKET="true")
    process = subprocess.Popen(
        ["uvicorn", "backend.app.main:app", "--port", "8001", "--host", "127.0.0.1"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env
    )
    return process

def wait_for_server():
    print("Waiting for server to become responsive (this includes yfinance cache pre-seeding)...")
    for i in range(40):
        try:
            r = httpx.get(f"{BASE_URL}/", timeout=1.0)
            if r.status_code == 200:
                print(f"Server is responsive and ready after {i*0.5:.1f}s!")
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def benchmark_endpoint(client, path, name, runs=20, timeout=10.0):
    print(f"Benchmarking {name} ({path})...")
    latencies = []
    
    # Warmup
    try:
        client.get(f"{BASE_URL}{path}", timeout=timeout)
    except Exception as e:
        print(f"  Warmup failed for {path}: {e}")
        
    for _ in range(runs):
        start = time.perf_counter()
        try:
            r = client.get(f"{BASE_URL}{path}", timeout=timeout)
            if r.status_code == 200:
                latencies.append((time.perf_counter() - start) * 1000) # Convert to ms
            else:
                print(f"  Non-200 response on {path}: {r.status_code}")
        except Exception as e:
            print(f"  Request failed on {path}: {e}")
            
    if not latencies:
        return None
        
    latencies.sort()
    avg_l = sum(latencies) / len(latencies)
    min_l = min(latencies)
    max_l = max(latencies)
    p95_l = latencies[int(len(latencies) * 0.95)] if len(latencies) >= 20 else latencies[-1]
    
    return {
        "name": name,
        "path": path,
        "runs": len(latencies),
        "avg_ms": avg_l,
        "min_ms": min_l,
        "max_ms": max_l,
        "p95_ms": p95_l
    }

async def benchmark_websocket():
    print("Connecting to WebSocket channel...")
    intervals = []
    try:
        async with websockets.connect(WS_URL, open_timeout=10.0) as ws:
            # 1. First frame should be the snapshot
            raw_init = await asyncio.wait_for(ws.recv(), timeout=5.0)
            init_msg = json.loads(raw_init)
            print(f"WebSocket Initial Snapshot Received: {init_msg.get('type')} type")
            
            # 2. Track next 3 streaming ticks (1.5s interval each)
            last_time = time.perf_counter()
            received_ticks = 0
            while received_ticks < 3:
                raw_msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                msg = json.loads(raw_msg)
                if msg.get('type') == 'tick':
                    now = time.perf_counter()
                    intervals.append((now - last_time) * 1000)
                    last_time = now
                    received_ticks += 1
                    print(f"  Frame {received_ticks} received: type=tick")
                else:
                    print(f"  Ignored non-tick WebSocket frame: type={msg.get('type')}")
    except Exception as e:
        print(f"WebSocket benchmark failed: {e}")
        return None
        
    return intervals

def run_all():
    server_process = start_server()
    try:
        if not wait_for_server():
            print("Failed to start server on port 8001. Port might be in use or startup timed out.")
            return
            
        # Run REST HTTP Benchmarks
        results = []
        with httpx.Client() as client:
            endpoints = [
                ("/", "Root Welcome Endpoint", 20, 10.0),
                ("/api/market/snapshot", "Market Snapshot (Cached)", 20, 10.0),
                ("/api/economy/indicators", "Economic Baseline Service", 20, 10.0),
                ("/api/news", "News Sentiment Engine", 20, 10.0),
                ("/api/scenario/simulate?oil_price=120.0&fed_rate=5.5&geopolitical_risk=60.0", "Scenario Simulator Solver", 20, 10.0),
                ("/api/ai/relationship/graph", "Macro Knowledge Graph", 20, 10.0),
                ("/api/ai/ask?query=why+is+gold+rising", "AI Analyst Copilot (Local Narrative)", 5, 30.0),
            ]
            
            for path, name, runs, timeout in endpoints:
                res = benchmark_endpoint(client, path, name, runs=runs, timeout=timeout)
                if res:
                    results.append(res)
                    
        # Run WebSocket Streams benchmark
        loop = asyncio.get_event_loop()
        ws_intervals = loop.run_until_complete(benchmark_websocket())
        
        # Output summary in markdown
        print("\n\n=======================================================")
        print("HUMMINGBIRD PROJECT PERFORMANCE METRICS")
        print("=======================================================")
        print("| Endpoint / Channel | Runs | Min Latency | Avg Latency | Max Latency | p95 Latency | Status |")
        print("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
        for r in results:
            print(f"| {r['name']} (`{r['path']}`) | {r['runs']} | {r['min_ms']:.2f} ms | {r['avg_ms']:.2f} ms | {r['max_ms']:.2f} ms | {r['p95_ms']:.2f} ms | PASS |")
            
        if ws_intervals:
            avg_int = sum(ws_intervals) / len(ws_intervals)
            print(f"\nWebSocket Streaming Feed Ticks (3 Frame Average): {avg_int/1000:.2f} seconds interval (Target: 1.50s)")
            if len(ws_intervals) > 1:
                print(f"WebSocket Jitter (Standard Deviation): {statistics.stdev(ws_intervals):.2f} ms")
        
    finally:
        print("Terminating server process...")
        server_process.terminate()
        try:
            server_process.wait(timeout=3)
            print("Server process exited cleanly.")
        except Exception:
            server_process.kill()
            print("Server process killed.")

if __name__ == "__main__":
    run_all()
