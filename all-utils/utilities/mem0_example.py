import os 
from dotenv import load_dotenv
from mem0 import Memory

# 1. SSL FIX
if "SSL_CERT_FILE" in os.environ:
    del os.environ["SSL_CERT_FILE"]


load_dotenv()


def run_observability_demo():
    # 2. CONFIGURATION
    config = {
        "vector_store": {
            "provider": "chroma", 
            "config": {"collection_name": "tech_demo", "path": "db"}
        },
        "llm": {
            "provider": "openai",
            "config": {"model": "gpt-4o-mini", "temperature": 0}
        }
    }

    # 3. INITIALIZE MEMORY
    m = Memory.from_config(config)

    user_id = "user_123"
    
    # 4. ADD DATA & CAPTURE ID
    print("\n--- [Step 2] Storing Initial Preference ---")
    result = m.add("I prefer using FastAPI and AWS.", user_id=user_id)


    # Robust ID Extraction
    mem_id = None
    if isinstance(result, list) and len(result) > 0:
        mem_id = result[0].get("id")
    elif isinstance(result, dict):
        # Check both possible locations for IDs
        res_list = result.get("results") or result.get("memories") or []
        if res_list:
            mem_id = res_list[0].get("id")


    
     # 5. UPDATE DATA
    print("--- [Step 3] Updating Preference (Triggering Change) ---")
    m.add("Actually, I've decided to move my projects to Google Cloud.", user_id=user_id)


    # 6. OBSERVABILITY: The History Report
    print("\n--- [Step 4] OBSERVABILITY REPORT: Memory Evolution ---")
    if mem_id:
        history = m.history(memory_id=mem_id)
        for entry in history:
            print(f"Event: {entry.get('event')}")
            old = entry.get('old_memory') or entry.get('old_value') or "Initial"
            new = entry.get('memory') or entry.get('new_value')
            print(f"Old: {old}")
            print(f"New: {new}")
            print("-" * 30)
    else:
        print("Note: Fact already exists or ID not captured. Check 'db' folder.")


    
    # 7. FINAL STATE: Search using the new FILTERS syntax
    print("\n--- [Step 5] Final State Check ---")
    # FIX: user_id must be in filters={}
    search_results = m.search(
        "What is my deployment preference?", 
        filters={"user_id": user_id}
    )
    
    # Handle search results (list vs dict)
    memories = search_results.get('results') if isinstance(search_results, dict) else search_results
    
    if memories:
        for res in memories:
            val = res.get('memory') or res.get('payload', {}).get('value')
            print(f"Observed Memory: {val} (Score: {res.get('score')})")
    else:
        print("No memories found for this user.")

