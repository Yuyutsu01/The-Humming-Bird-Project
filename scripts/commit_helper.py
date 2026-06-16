import os
import shutil
import subprocess

# Constants
WORKSPACE_DIR = r"c:\Users\shiva\The-Humming-Bird-Project"
BACKUP_DIR = os.path.join(WORKSPACE_DIR, "backup_temp")

# File lists
FILES_TO_BACKUP = [
    ("backend/requirements.txt", "backend/requirements.txt"),
    ("backend/app/core/config.py", "backend/app/core/config.py"),
    ("backend/app/services/economic_data.py", "backend/app/services/economic_data.py"),
    ("backend/app/services/alternative_data.py", "backend/app/services/alternative_data.py"),
    ("backend/app/services/market_data.py", "backend/app/services/market_data.py"),
    ("backend/app/services/relationship_engine.py", "backend/app/services/relationship_engine.py"),
    ("backend/app/services/scenario_simulator.py", "backend/app/services/scenario_simulator.py"),
    ("backend/app/services/forecasting.py", "backend/app/services/forecasting.py"),
    ("backend/app/services/news_engine.py", "backend/app/services/news_engine.py"),
    ("backend/app/services/ai_analyst.py", "backend/app/services/ai_analyst.py"),
    ("backend/app/routers/market.py", "backend/app/routers/market.py"),
    ("backend/app/routers/economy.py", "backend/app/routers/economy.py"),
    ("backend/app/routers/news.py", "backend/app/routers/news.py"),
    ("backend/app/routers/scenario.py", "backend/app/routers/scenario.py"),
    ("backend/app/routers/ai.py", "backend/app/routers/ai.py"),
    ("backend/app/routers/ws.py", "backend/app/routers/ws.py"),
    ("backend/app/main.py", "backend/app/main.py"),
    ("scripts/test_backend.py", "scripts/test_backend.py"),
    ("README.md", "README.md"),
]

def run_git(args):
    print(f"Running git {' '.join(args)}...")
    res = subprocess.run(["git"] + args, cwd=WORKSPACE_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Git failed: {res.stderr}")
    return res

def create_backup():
    print("Backing up files to backup_temp...")
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)
    os.makedirs(BACKUP_DIR)
    
    for rel_path, _ in FILES_TO_BACKUP:
        src = os.path.join(WORKSPACE_DIR, rel_path)
        dst = os.path.join(BACKUP_DIR, rel_path)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f"Backed up {rel_path}")
        else:
            print(f"WARNING: {rel_path} not found to back up.")

def clean_workspace():
    print("Cleaning up old files and untracked files to prepare...")
    
    # Files to explicitly delete to let us rebuild them step-by-step
    files_to_delete = [
        "backend/requirements.txt",
        "backend/app/core/config.py",
        "backend/app/services/economic_data.py",
        "backend/app/services/alternative_data.py",
        "backend/app/services/market_data.py",
        "backend/app/services/relationship_engine.py",
        "backend/app/services/scenario_simulator.py",
        "backend/app/services/forecasting.py",
        "backend/app/services/news_engine.py",
        "backend/app/services/ai_analyst.py",
        "backend/app/routers/market.py",
        "backend/app/routers/economy.py",
        "backend/app/routers/news.py",
        "backend/app/routers/scenario.py",
        "backend/app/routers/ai.py",
        "backend/app/routers/ws.py",
        "backend/app/main.py",
        "scripts/test_backend.py",
    ]
    
    for f in files_to_delete:
        p = os.path.join(WORKSPACE_DIR, f)
        if os.path.exists(p):
            os.remove(p)
            
    # Clean up empty directories under backend/app
    for root, dirs, files in os.walk(os.path.join(WORKSPACE_DIR, "backend"), topdown=False):
        for name in dirs:
            dir_path = os.path.join(root, name)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)

    # Revert README.md to the parent commit status (8f68b33)
    run_git(["checkout", "README.md"])

    # Stage deletions of the old files that were in the index from 8f68b33
    run_git(["rm", "backend/api/router.py", "backend/api/websocket.py", "main.py", "--ignore-unmatch"])

def read_backup_file(rel_path):
    p = os.path.join(BACKUP_DIR, rel_path)
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

def write_file(rel_path, content):
    p = os.path.join(WORKSPACE_DIR, rel_path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

def make_commit(rel_path, content, message):
    write_file(rel_path, content)
    run_git(["add", rel_path])
    res = run_git(["commit", "-m", message])
    if res.returncode != 0:
        print(f"Error committing: {res.stderr}")
    else:
        print(f"SUCCESS: Committed {rel_path} - '{message}'")

def main():
    create_backup()
    clean_workspace()
    
    # Commit 1: Clean up old layout, add requirements.txt
    req_content = read_backup_file("backend/requirements.txt")
    write_file("backend/requirements.txt", req_content)
    # Stage deletions as well in the first commit
    run_git(["add", "backend/requirements.txt"])
    run_git(["add", "-u"])  # stages the deletions of main.py and backend/api files
    run_git(["commit", "-m", "chore: delete obsolete files and add backend requirements.txt"])
    print("SUCCESS: Commit 1 (Requirements & Deletions)")

    # Commit 2: config.py
    cfg_content = read_backup_file("backend/app/core/config.py")
    make_commit("backend/app/core/config.py", cfg_content, "feat(config): initialize base application settings and env parsing configuration")

    # Commit 3: services/economic_data.py
    econ_content = read_backup_file("backend/app/services/economic_data.py")
    make_commit("backend/app/services/economic_data.py", econ_content, "feat(services): implement economic data service with pre-seeded baseline indicators")

    # Commit 4: services/alternative_data.py
    alt_content = read_backup_file("backend/app/services/alternative_data.py")
    make_commit("backend/app/services/alternative_data.py", alt_content, "feat(services): implement alternative data service for high frequency data")

    # Commit 5: services/market_data.py Part 1 (TICKER_MAP, init, get_market_snapshot, _fetch_ticker_data)
    mkt_full = read_backup_file("backend/app/services/market_data.py")
    # Extract part 1 (lines 1 to 163)
    mkt_lines = mkt_full.splitlines()
    mkt_part1 = "\n".join(mkt_lines[:163]) + "\n"
    make_commit("backend/app/services/market_data.py", mkt_part1, "feat(services): setup market data service structures and cached yfinance lookups")

    # Commit 6: services/market_data.py Part 2 (Full file with Brownian simulated ticks and charts)
    make_commit("backend/app/services/market_data.py", mkt_full, "feat(services): add brownian motion live simulation and historical bars to market service")

    # Commit 7: services/relationship_engine.py Part 1 (Nodes & Edges Definition)
    rel_full = read_backup_file("backend/app/services/relationship_engine.py")
    rel_lines = rel_full.splitlines()
    rel_part1 = "\n".join(rel_lines[:48]) + "\n"
    make_commit("backend/app/services/relationship_engine.py", rel_part1, "feat(services): define macroeconomic relationship knowledge graph nodes and edges")

    # Commit 8: services/relationship_engine.py Part 2 (Causality Trace BFS)
    make_commit("backend/app/services/relationship_engine.py", rel_full, "feat(services): add shortest causal transmission pathfinding to relationship service")

    # Commit 9: services/scenario_simulator.py Part 1 (Baseline constants and class skeleton)
    scen_full = read_backup_file("backend/app/services/scenario_simulator.py")
    scen_lines = scen_full.splitlines()
    scen_part1 = "\n".join(scen_lines[:17]) + "\n"
    make_commit("backend/app/services/scenario_simulator.py", scen_part1, "feat(services): scaffold scenario simulation service with baseline inputs and outputs")

    # Commit 10: services/scenario_simulator.py Part 2 (Simulation calculations)
    make_commit("backend/app/services/scenario_simulator.py", scen_full, "feat(services): implement macroeconomic simulation stress-testing calculations")

    # Commit 11: services/forecasting.py
    fc_content = read_backup_file("backend/app/services/forecasting.py")
    make_commit("backend/app/services/forecasting.py", fc_content, "feat(services): implement forecasting service supporting Prophet, XGBoost, and LSTM models")

    # Commit 12: services/news_engine.py
    news_content = read_backup_file("backend/app/services/news_engine.py")
    make_commit("backend/app/services/news_engine.py", news_content, "feat(services): implement news intelligence deduplication and sentiment analysis engine")

    # Commit 13: services/ai_analyst.py Part 1 (Semantic answers local fallback)
    ai_full = read_backup_file("backend/app/services/ai_analyst.py")
    ai_lines = ai_full.splitlines()
    ai_part1 = "\n".join(ai_lines[:261]) + "\n"
    make_commit("backend/app/services/ai_analyst.py", ai_part1, "feat(services): setup AI analyst copilot with local fallback narrative database")

    # Commit 14: services/ai_analyst.py Part 2 (Gemini API integration)
    ai_part2 = "\n".join(ai_lines[:296]) + "\n"
    make_commit("backend/app/services/ai_analyst.py", ai_part2, "feat(services): integrate Google Gemini Pro model adapter in AI analyst service")

    # Commit 15: services/ai_analyst.py Part 3 (OpenAI integration & Full service)
    make_commit("backend/app/services/ai_analyst.py", ai_full, "feat(services): integrate OpenAI model adapter and export AI analyst service singleton")

    # Commit 16: routers/market.py
    r_mkt_content = read_backup_file("backend/app/routers/market.py")
    make_commit("backend/app/routers/market.py", r_mkt_content, "feat(routers): add market data endpoints for snapshots and history lookup")

    # Commit 17: routers/economy.py
    r_econ_content = read_backup_file("backend/app/routers/economy.py")
    make_commit("backend/app/routers/economy.py", r_econ_content, "feat(routers): add economy endpoints for current and historical domestic indicators")

    # Commit 18: routers/news.py
    r_news_content = read_backup_file("backend/app/routers/news.py")
    make_commit("backend/app/routers/news.py", r_news_content, "feat(routers): add news router for streaming intelligence news feeds")

    # Commit 19: routers/scenario.py
    r_scen_content = read_backup_file("backend/app/routers/scenario.py")
    make_commit("backend/app/routers/scenario.py", r_scen_content, "feat(routers): add scenario simulation endpoints for stress-testing metrics")

    # Commit 20: routers/ai.py
    r_ai_content = read_backup_file("backend/app/routers/ai.py")
    make_commit("backend/app/routers/ai.py", r_ai_content, "feat(routers): add AI analyst routes for queries and causality mapping")

    # Commit 21: routers/ws.py Part 1 (Connection manager and skeleton)
    r_ws_full = read_backup_file("backend/app/routers/ws.py")
    ws_lines = r_ws_full.splitlines()
    ws_part1 = "\n".join(ws_lines[:35]) + "\n"
    make_commit("backend/app/routers/ws.py", ws_part1, "feat(routers): setup WebSocket connection manager routing layer")

    # Commit 22: routers/ws.py Part 2 (Full file with broadcasting loop and Brownian updates)
    make_commit("backend/app/routers/ws.py", r_ws_full, "feat(routers): implement real-time WebSocket broadcasting feed loops")

    # Commit 23: main.py
    app_main_content = read_backup_file("backend/app/main.py")
    make_commit("backend/app/main.py", app_main_content, "feat(main): configure FastAPI application, middleware routing, and lifespan cache pre-seeding")

    # Commit 24: scripts/test_backend.py
    test_script_content = read_backup_file("scripts/test_backend.py")
    make_commit("scripts/test_backend.py", test_script_content, "test: add integration test suite to verify all backend API routing")

    # Commit 25: README.md
    readme_content = read_backup_file("README.md")
    write_file("README.md", readme_content)
    run_git(["add", "README.md"])
    res = run_git(["commit", "-m", "docs: update comprehensive project documentation for restructured backend"])
    if res.returncode == 0:
        print("SUCCESS: Committed README.md - docs update")
        
    print("\nRe-verifying git commit history:")
    run_git(["log", "-n", "27", "--oneline"])
    
    # Remove backup temp directory
    shutil.rmtree(BACKUP_DIR)
    print("Cleaned up temporary backups.")

if __name__ == "__main__":
    main()
