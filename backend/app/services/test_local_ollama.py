import asyncio
import sys
import os

# Adjust path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from backend.app.services.ai_analyst import ai_analyst_service

async def run_test():
    print("==================================================")
    print("TESTING LOCAL OLLAMA CONNECTION WITH AI ANALYST...")
    print("==================================================")
    
    test_query = "Why is gold rising?"
    print(f"Sending query: '{test_query}'")
    
    try:
        response = await ai_analyst_service.ask_question(test_query)
        print("\n[SUCCESS] Response received from AI Analyst!")
        print(f"Engine used: {response.get('engine')}")
        print(f"Title: {response.get('title')}")
        print(f"Summary: {response.get('summary')}")
        print(f"Cause: {response.get('cause')}")
        print(f"Effect: {response.get('effect')}")
        
        # Verify structure
        assert "india_impact" in response, "Missing 'india_impact'"
        assert isinstance(response["india_impact"], list), "'india_impact' must be a list"
        assert "details" in response, "Missing 'details'"
        assert isinstance(response["details"], dict), "'details' must be a dictionary"
        
        details = response["details"]
        for key in ["root_cause", "risks", "opportunities", "historical_comparison", "predictions"]:
            assert key in details, f"Missing details subkey: '{key}'"
            
        print("\n[PASS] All schema structure assertions passed successfully!")
        print("Detailed response keys and structure are fully validated!")
        
    except Exception as e:
        print(f"\n[FAIL] Test encountered an error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_test())
