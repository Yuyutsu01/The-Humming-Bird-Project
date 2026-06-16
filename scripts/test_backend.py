import sys
import httpx

BASE_URL = "http://127.0.0.1:8000/api"

def run_tests():
    print("===========================================")
    print("STARTING BACKEND API VERIFICATION TESTS...")
    print("===========================================\n")
    
    # 1. Test Root
    try:
        r = httpx.get("http://127.0.0.1:8000/")
        assert r.status_code == 200
        print("[PASS] Root Endpoint Status: Active")
    except Exception as e:
        print(f"[FAIL] Root Endpoint check. Make sure server is running. Error: {e}")
        sys.exit(1)

    # 2. Test Market Snapshot
    try:
        r = httpx.get(f"{BASE_URL}/market/snapshot")
        assert r.status_code == 200
        data = r.json()
        assert "indian_markets" in data
        assert "global_markets" in data
        assert "Nifty 50" in data["indian_markets"]
        print(f"[PASS] Market Snapshot verification. Nifty 50 Price: {data['indian_markets']['Nifty 50']['price']}")
    except Exception as e:
        print(f"[FAIL] Market Snapshot check: {e}")
        sys.exit(1)

    # 3. Test Economic Indicators
    try:
        r = httpx.get(f"{BASE_URL}/economy/indicators")
        assert r.status_code == 200
        data = r.json()
        assert "india" in data
        assert "CPI Inflation" in data["india"]
        print(f"[PASS] Economic Indicators verification. Current CPI: {data['india']['CPI Inflation']['current']}%")
    except Exception as e:
        print(f"[FAIL] Economic Indicators check: {e}")
        sys.exit(1)

    # 4. Test AI Analyst (Why is gold rising?)
    try:
        r = httpx.get(f"{BASE_URL}/ai/ask?query=Why+is+gold+rising")
        assert r.status_code == 200
        data = r.json()
        assert "title" in data
        assert "india_impact" in data
        print(f"[PASS] AI Analyst verification. Title: '{data['title']}'")
        print(f"       Engine: {data['engine']}")
    except Exception as e:
        print(f"[FAIL] AI Analyst check: {e}")
        sys.exit(1)

    # 5. Test Scenario Simulator (Oil at $120)
    try:
        r = httpx.get(f"{BASE_URL}/scenario/simulate?oil_price=120.0&fed_rate=5.25&geopolitical_risk=50.0")
        assert r.status_code == 200
        data = r.json()
        assert "metrics" in data
        assert "cpi_inflation" in data["metrics"]
        print(f"[PASS] Scenario Simulator verification. Simulated CPI at $120 Oil: {data['metrics']['cpi_inflation']['value']}% (vs Baseline: {data['metrics']['cpi_inflation']['baseline']}%)")
    except Exception as e:
        print(f"[FAIL] Scenario Simulator check: {e}")
        sys.exit(1)

    print("\n===========================================")
    print("ALL BACKEND VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("===========================================")

if __name__ == "__main__":
    run_tests()
