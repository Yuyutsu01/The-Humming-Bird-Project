# Architectural Analysis & Reverse Engineering Report: OpenTerminal (The Hummingbird Project)

---

## 1. Executive Summary
OpenTerminal (internally codenamed the **Hummingbird Project**) is a high-density, cinematic macroeconomic intelligence terminal. It functions as a decoupled client-server Single-Page Application (SPA) designed to model, simulate, and visualize the transmission of global macroeconomic developments and geopolitical conflicts into domestic transmission channels affecting the Indian economy and markets. 

The system leverages a modern Next.js desktop client utilizing a dark-mode glassmorphic theme to deliver an institutional-grade feel. Behind the client sits a high-performance FastAPI backend engine. This engine exposes REST APIs and a WebSocket stream to broadcast simulated ticks (using Brownian random walks), execute macro econometric sensitivity simulations, compute shortest causal pathways in an economic knowledge graph, and orchestrate queries through a multi-tiered AI Analyst Copilot (featuring fallback logic ranging from Google Gemini to local Ollama instances and rule-based template matchers).

---

## 2. Project Purpose & Problem Solved
Retail investors, financial analysts, and economics students frequently struggle to comprehend the complex, multi-layered pathways through which global macroeconomic shocks impact their domestic markets. 

### The Problem
Traditional market terminals (such as Bloomberg or Reuters Eikon) are highly gatekept by exorbitant subscription costs ($24,000+/year), making them inaccessible to retail consumers. Meanwhile, free consumer interfaces (like Yahoo Finance or trading portals) present data in isolation, failing to model or visualize the causal propagation of macro variables (e.g., how a rise in Brent Crude prices triggers imported inflation, prompting central bank rate hikes that compress corporate earnings and drag down equity markets).

### The Solution
OpenTerminal bridges this gap by offering a free, open-source architectural blueprint of a financial workstation. It provides:
1. **Interactive Stress Testing**: Let users input global shocks (Brent Crude spikes, US Fed interest rate hikes, Geopolitical risk index surges) and view simulated domestic adjustments (USD/INR exchange rate, CPI inflation, RBI repo rate, GDP growth, and Nifty 50 valuations) in real time.
2. **Causality Graph Visualization**: Maps the macroeconomic transmission channels via an interactive SVG node-link graph and traces the shortest propagation pathways between variables.
3. **AI Copilot Narratives**: Bridges quantitative metrics with qualitative text reports using local or external Large Language Models (LLMs) with robust semantic offline fallback capabilities.

---

## 3. Business Logic & Macroeconomic Modeling
The platform operates on empirical macroeconomic transmission models. There are three primary transmission channels modeled in the codebase:

```
[Global Trigger] 
       ↓
[Transmission Channel] 
       ↓
[Domestic Macro Output] 
       ↓
[Sector Sensitivity Index]
```

### Transmission Channels

#### A. The Commodity Price Channel (Energy Shock)
* **Trigger**: A rise in Brent Crude prices.
* **Mechanism**: India imports over 85% of its crude oil requirements. When global oil prices surge:
  1. The merchandise import bill swells, widening the Current Account Deficit (CAD) and increasing demand for US Dollars, which depreciates the Indian Rupee (INR).
  2. Transport and manufacturing input costs rise immediately, creating cost-push CPI inflation.
  3. Margin compression hits import-dependent sectors (Aviation due to Aviation Turbine Fuel costs, Paints & Chemicals due to oil-derivative raw materials, and Automotive due to fuel prices depressing consumer purchase interest).
  4. Upstream energy explorers (ONGC, Oil India) benefit from higher crude realizations.

#### B. The Interest Rate Differential Channel (Capital Flow Shock)
* **Trigger**: The US Federal Reserve hikes interest rates.
* **Mechanism**: 
  1. Rising risk-free US Treasury yields compress the spread between Indian government bonds and US assets.
  2. Foreign Institutional Investors (FIIs) engage in capital flight, selling Indian equities/debt and converting capital to USD.
  3. Rupee depreciation increases imported inflation (imported goods cost more in local currency).
  4. To anchor inflation expectations and defend the exchange rate, the Reserve Bank of India (RBI) is pressured to keep domestic policy (Repo) rates elevated, raising the borrowing cost of capital for Indian corporations and consumers.
  5. Higher interest rates increase discount factors, dragging down equity multiples (Nifty 50), while expanding retail loan EMIs (harming automotive and real estate sectors). Export-oriented IT services benefit from a weaker rupee due to dollar revenues.

#### C. The Safe-Haven Asset Channel (Geopolitical Risk Shock)
* **Trigger**: Geopolitical Risk Index surges (e.g., Red Sea shipping corridor disruptions).
* **Mechanism**:
  1. Instability triggers global risk aversion, driving capital flows to safe-haven assets (Gold, US Dollar DXY).
  2. Gold prices surge, bloating India's gold import bill (expanding trade deficit).
  3. Household wealth rises due to physical gold holdings (benefiting Gold Loan NBFCs), but retail jewelry transaction volumes contract.
  4. Rerouting cargo via the Cape of Good Hope increases freight shipping rates and delays tech hardware component imports (semiconductors).

---

## 4. Complete Tech Stack

| Technology | Category | Version | Purpose in Project | Interactions & Data Flow | Alternatives |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Next.js** | Frontend Framework | `16.2.7` | Provides the Single Page Application structure, App Router routing, and client-side page rendering. | Hosts the dashboard views; establishes WebSockets connections to the backend server. | Vite + React, Nuxt.js, SvelteKit |
| **React** | Core UI Library | `19.2.4` | Enables component-based UI design and state hooks management. | Handles dashboard selections, slider state changes, and chat history renders. | Vue.js, Angular, SolidJS |
| **Tailwind CSS** | CSS Framework | `^4.0.0` | Implements glassmorphic UI design, layouts, and animations. | Integrated with PostCSS (`@tailwindcss/postcss`) to compile global terminal classes. | Vanilla CSS, Sass, Bootstrap, styled-components |
| **FastAPI** | Backend Web Framework | `>=0.110.0` | High-performance async ASGI web framework for Python. | Exposes REST endpoints for calculations/AI queries, and WebSocket channels for ticks. | Flask, Django REST Framework, Express.js |
| **Uvicorn** | ASGI Server | `>=0.28.0` | Light-speed execution runner for ASGI applications. | Listens on port 8000 (dev) and coordinates request/response threads. | Hypercorn, Gunicorn, Daphne |
| **yfinance** | Financial Data | `>=0.2.37` | Fetches historical price bars and real-time market snapshots. | Queried on server lifespan startup to pre-seed the market data cache. | Alpha Vantage, IEX Cloud, Quandl, Bloomberg API |
| **Pandas** | Data Wrangling | `>=2.2.1` | Manages time-series dataframes for charting and modeling. | Calculates calendar intervals and shapes data frames in `MarketDataService`. | Polars, NumPy, Dask |
| **NumPy** | Mathematics | `>=1.26.4` | Mathematical array processing. | Drives time-delta computations and shape arrays in forecasting modules. | SciPy, Standard Math library |
| **SciPy** | Statistical Analysis | `>=1.12.0` | Advanced scientific computing. | Power-functions regression and sensitivity models. | Statsmodels, scikit-learn |
| **Websockets** | Real-time Streaming | `>=12.0` | Native Python WebSocket implementation. | Handles persistent client connections for streaming live Brownian ticks. | Socket.io, SSE (Server-Sent Events) |
| **Httpx** | Async HTTP Client | `>=0.27.0` | Async REST client for external API requests. | Communicates asynchronously with Gemini/OpenAI endpoints. | Requests, Aiohttp |
| **Pydantic** | Data Validation | `>=2.6.4` | Validates data schemas and configurations. | Enforces strict schemas for config settings and models. | Marshmallow, Cerberus |
| **Pydantic-Settings** | Configuration | `>=2.2.1` | Environment settings management. | Parses system configurations from the `.env` file. | Python-dotenv, Configparser |
| **Google Gemini API** | AI Integration | *Latest* | Generates natural language economic analyses. | Leveraged by `AIAnalystService` as the primary cognitive routing layer. | OpenAI GPT, Anthropic Claude |
| **OpenAI GPT API** | AI Integration | *Latest* | Generates natural language economic analyses (secondary). | Leveraged by `AIAnalystService` as the secondary cognitive routing layer. | Google Gemini, Cohere |
| **Ollama** | Local AI Core | *Latest* | Runs local LLM instances (Llama 3.2, Mistral). | Serves as the tertiary local AI engine fallback when API keys are absent. | Llama.cpp, Local HuggingFace Transformers |

---

## 5. Architecture
The project follows a **Decoupled Client-Server Client-Side Orchestration Architecture**:

```
                  ┌──────────────────────┐
                  │   Next.js Client     │
                  │   (globals.css)      │
                  └──────────┬───────────┘
               HTTP REST     │     WebSockets
               GET requests  │     Live Ticks
                             ▼
                  ┌──────────────────────┐
                  │    FastAPI Server    │
                  │       (Lifespan)     │
                  └──────────┬───────────┘
                             │
       ┌─────────────────────┼─────────────────────┐
       ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│Market Service│     │Scenario Serv.│     │  AI Analyst  │
│ (yfinance)   │     │ (Regressions)│     │(Gemini/Ollama│
└──────────────┘     └──────────────┘     └──────────────┘
```

### Architectural Decisions & Trade-offs

* **In-Memory Caching & Lifespan Hooks**: On backend startup, a lifespan context manager (`lifespan` in `app/main.py`) calls `market_data_service.get_market_snapshot()`. This fetches data for 30+ symbols from `yfinance` in a separate thread pool (preventing async blocking) and caches it. 
  * *Advantage*: High speed; subsequent API calls hit local memory.
  * *Disadvantage*: Slow cold start (~5-10s to fetch all tickers); memory state is lost on server restart.
* **Brownian Motion Live Tick Generation**: Once connected to the `/api/ws` WebSocket channel, the client receives initial cached snapshot data. The server then executes a loop every 1.5 seconds: generating normal-distribution perturbations (Brownian random walk) on the active ticker prices and broadcasting them.
  * *Advantage*: Simulate real-time ticking feeds without incurring financial API subscription costs.
  * *Disadvantage*: Ticks are synthetic fluctuations, not reflective of real intraday trading volumes.
* **Debounced Rest Simulations**: Slider adjustments in `SimulatorPanel.tsx` trigger REST requests to `/api/scenario/simulate`. The request is debounced by 200ms on the frontend.
  * *Advantage*: Prevents network spam and server load during active slider movements.
  * *Disadvantage*: Slight input lag (~200ms) before simulated outputs update on-screen.
* **Cohesion & Coupling**: Highly cohesive services singleton modules (`EconomicDataService`, `MarketDataService`, `ScenarioSimulatorService`, `AIAnalystService`). However, tight coupling exists in `AIAnalystService`'s dependency on global configuration variables parsed by Pydantic.

---

## 6. Folder Structure Analysis
A deep inspection of the repository folders reveals the following structural organization:

```
OpenTerminal/
├── backend/                              # FastAPI Service Core
│   ├── app/                              # Active Application Directory
│   │   ├── core/                         # Core Settings
│   │   │   └── config.py                 # Configuration manager (Pydantic-Settings)
│   │   ├── routers/                      # HTTP/WS API Routers
│   │   │   ├── ai.py                     # Analyst queries & causality routes
│   │   │   ├── economy.py                # Economic indicators & forecasting routes
│   │   │   ├── market.py                 # Snapshot & chart data routes
│   │   │   ├── news.py                   # News intelligence feed route
│   │   │   ├── scenario.py               # Stress-test simulation route
│   │   │   └── ws.py                     # WebSocket Connection Manager & ticker loop
│   │   ├── services/                     # Business Logic Engines
│   │   │   ├── ai_analyst.py             # LLM router and semantic rule-base
│   │   │   ├── alternative_data.py       # High-frequency data (port traffic, satellite index)
│   │   │   ├── economic_data.py          # Baseline Indian macro indicators seed
│   │   │   ├── forecasting.py            # Prophet/LSTM mock forecasting trends
│   │   │   ├── market_data.py            # yfinance fetcher and Brownian simulation
│   │   │   ├── news_engine.py            # Deduplicating news sentiment analyzer
│   │   │   ├── relationship_engine.py    # Causal graph paths tracer (BFS/DFS)
│   │   │   └── test_local_ollama.py      # Schema verification helper for local models
│   │   └── main.py                       # FastAPI startup coordinator & lifespan manager
│   ├── services/                         # Dead Code: Obsolete prototype folder
│   │   ├── market_data.py                # Prototype market fetcher (unused)
│   │   └── oms.py                        # Prototype Order Management System (unused)
│   ├── .env                              # Local environment keys configuration
│   ├── main.py                           # Dead Code: Obsolete root main entrypoint
│   └── requirements.txt                  # Python dependencies
│
├── frontend/                             # Next.js Application Core
│   ├── src/                              # Source Directory
│   │   ├── app/                          # Next.js App Router Pages
│   │   │   ├── globals.css               # PostCSS Tailwind and terminal styling
│   │   │   ├── layout.tsx                # Page shell and SEO metadata
│   │   │   └── page.tsx                  # Main terminal workspace (WebSockets host)
│   │   └── components/                   # Reusable React UI widgets
│   │       ├── AICopilot/                # AI drawer & causal graphic panels
│   │       │   ├── CopilotPanel.tsx      # Sidebar chat drawer component
│   │       │   └── MacroGraph.tsx        # Causal SVG visualizer component
│   │       ├── Dashboards/               # Tabbed Role dashboards
│   │       │   ├── EconomistDashboard.tsx # Historical charts & AI Forecasting
│   │       │   ├── GovernmentDashboard.tsx # Shipping and satellite alternative indicators
│   │       │   ├── InvestorDashboard.tsx # Correlation matrix & custom candles chart
│   │       │   ├── ResearchDashboard.tsx # Geopolitical risks timelines
│   │       │   └── StudentDashboard.tsx  # Slidewise lesson sandbox & quizzes
│   │       ├── ScenarioSimulator/        # Econometric simulation sliders
│   │       │   └── SimulatorPanel.tsx    # Slider controller panel component
│   │       └── CommandBar.tsx            # Global Omnibox keyboard interface
│   ├── package.json                      # Node packages configurations
│   ├── tsconfig.json                     # TypeScript configurations
│   └── ...                               # Configuration files
│
└── scripts/                              # Dev utilities and test files
    ├── commit_helper.py                  # Commits history rebuild generator
    ├── performance_benchmark.py          # Latency & ws jitter benchmark runner
    └── test_backend.py                   # Integration testing suite
```

### Dead Code & Duplicate Logic Identification
* **`backend/main.py` (Unused)**: This file is obsolete. It imports `api.router` and `api.websocket`, neither of which exist in the modern directory structure. The active entry point is `backend/app/main.py`.
* **`backend/services/` (Unused)**: This directory is dead code. The file `backend/services/market_data.py` is a simplified prototype. The active file is `backend/app/services/market_data.py`. The mock Order Management System (`backend/services/oms.py`) is completely unused and has no active imports in the app.
* **`backend/__pycache__/main.cpython-311.pyc`**: Tracked in Git by accident. Should be ignored via `.gitignore` and removed from tracking.

---

## 7. Detailed Source Code Walkthrough

### 1. Backend Startup & Cache Initialization
* **File**: `backend/app/main.py`
* **Logic**: Uses FastAPI's `lifespan` context manager. On startup, it triggers `market_data_service.get_market_snapshot()`. This fetches actual asset prices via `yfinance` for symbols mapped in `TICKER_MAP`.

```python
# From backend/app/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Indian Economic Intelligence Platform Backend...")
    try:
        # Pre-seed cache with initial snapshot from yfinance
        await market_data_service.get_market_snapshot()
        logger.info("Market data cache pre-seeded successfully.")
    except Exception as e:
        logger.error(f"Failed to pre-seed market cache: {e}")
    yield
    logger.info("Shutting down backend services.")
```

### 2. Multi-Tiered AI Routing & Semantic Fallback
* **File**: `backend/app/services/ai_analyst.py`
* **Logic**: Resolves natural language queries by traversing a priority sequence of LLM providers. If API keys and local Ollama are unavailable, it uses regex to match queries against `SEMANTIC_ANSWERS` (a dictionary of pre-constructed, high-quality economic reports).

```python
# From backend/app/services/ai_analyst.py
async def ask_question(self, query: str) -> dict:
    query_lower = query.lower()
    
    # Tier 1: Google Gemini (if API Key exists)
    if settings.GEMINI_API_KEY:
        try:
            return await self._call_gemini_api(query)
        except Exception as e:
            logger.error(f"Gemini API failed: {e}")
            
    # Tier 2: OpenAI GPT-4 (if API Key exists)
    if settings.OPENAI_API_KEY:
        try:
            return await self._call_openai_api(query)
        except Exception as e:
            logger.error(f"OpenAI API failed: {e}")
            
    # Tier 3: Local Ollama (if USE_OLLAMA is True)
    if settings.USE_OLLAMA:
        try:
            return await self._call_ollama_api(query)
        except Exception as e:
            logger.error(f"Ollama local LLM failed: {e}")

    # Tier 4: Rule-based Semantic Keyword Fallback
    matched_key = None
    if "gold" in query_lower:
        matched_key = "gold"
    elif "oil" in query_lower:
        matched_key = "oil"
    # ... more keywords
    
    if matched_key:
        data = SEMANTIC_ANSWERS[matched_key]
        return {
            "engine": "Local Narrative engine (Fallback)",
            "query": query,
            **data
        }
        
    # Tier 5: Catch-all Generic Synthesis
    return self._generate_generic_economic_response(query)
```

### 3. Jaccard-Similarity News Deduplication
* **File**: `backend/app/services/news_engine.py`
* **Logic**: Deduplicates incoming feeds by calculating Jaccard similarity coefficients between tokenized headlines (excluding common stop words). If the similarity index is greater than `0.4`, it flags the items as duplicates and retains only the one with the longer content body.

```python
# From backend/app/services/news_engine.py
def _deduplicate(self, articles: list[dict]) -> list[dict]:
    unique_articles = []
    for art in articles:
        is_dup = False
        art_words = self._tokenize(art["title"])
        
        for u_art in unique_articles:
            u_words = self._tokenize(u_art["title"])
            # Calculate Jaccard similarity: intersection over union
            intersection = len(art_words.intersection(u_words))
            union = len(art_words.union(u_words))
            similarity = intersection / union if union > 0 else 0
            
            if similarity > 0.4:
                is_dup = True
                # Keep the longer article
                if len(art["content"]) > len(u_art["content"]):
                    unique_articles.remove(u_art)
                    unique_articles.append(art)
                break
        if not is_dup:
            unique_articles.append(art)
    return unique_articles
```

---

## 8. Data Flow
Below are step-by-step traces of data propagation through the client-server system.

### A. Live Market Tick Stream (WebSockets)
```
[FastAPI Server Background Loop]
             ↓ (Every 1.5 seconds)
[MarketDataService.generate_simulated_ticks()]
             ↓ (Perturb active prices using Brownian motion)
[ws.py WebSocket Endpoint]
             ↓ (Wrap in JSON: {"type": "tick", "data": ...})
[Next.js Client: Home Component (ws.onmessage)]
             ↓ (Update `liveTicks` state)
[InvestorDashboard (Merge liveTicks into local state)]
             ↓ (Flash row green/red based on direction)
[Renders Updated Spot Price in UI]
```

### B. Scenario Stress Testing (REST HTTP)
```
[User drags slider in SimulatorPanel]
             ↓ (Change oilPrice / fedRate / geoRisk)
[Debounce delay: 200ms]
             ↓
[Fetch GET /api/scenario/simulate?oil_price=...&fed_rate=...]
             ↓
[FastAPI: scenario.py Route Handler]
             ↓
[ScenarioSimulatorService.simulate()]
             ↓ (Calculate offsets based on econometric formulas)
[Format output JSON response containing metrics and sector scores]
             ↓
[Next.js Client: SimulatorPanel (setResult)]
             ↓ (Update cards and progress bars)
[Renders Simulated Macro Targets and Sector Heatmap]
```

---

## 9. API Documentation

### HTTP REST API

#### 1. Market Snapshot
* **Route**: `GET /api/market/snapshot`
* **Purpose**: Fetches the latest price and change percentage for all tracked assets.
* **Authentication**: None.
* **Input**: None.
* **Output (200 OK)**:
  ```json
  {
    "indian_markets": {
      "Nifty 50": {
        "ticker": "^NSEI",
        "price": 22800.0,
        "change_pct": 0.75,
        "timestamp": "2026-07-22T16:51:12"
      }
    },
    "commodities": {
      "Brent Crude": {
        "ticker": "BZ=F",
        "price": 82.50,
        "change_pct": -0.9,
        "timestamp": "2026-07-22T16:51:12"
      }
    }
    // global_markets, forex, bonds
  }
  ```

#### 2. Market History
* **Route**: `GET /api/market/history`
* **Purpose**: Returns historical OHLCV data for charting.
* **Query Parameters**:
  * `name`: string (e.g. `Nifty 50`, `Gold`)
  * `period`: string (`1mo` default, `3mo`, `1y`)
  * `interval`: string (`1d` default, `1wk`, `1mo`)
* **Output (200 OK)**:
  ```json
  [
    {
      "date": "2026-06-22",
      "open": 22750.0,
      "high": 22820.0,
      "low": 22710.0,
      "close": 22800.0,
      "volume": 350000
    }
  ]
  ```

#### 3. Scenario Simulation
* **Route**: `GET /api/scenario/simulate`
* **Purpose**: Simulates the domestic impact of changes in global variables.
* **Query Parameters**:
  * `oil_price`: float (range: `40.0` to `200.0`, default: `82.50`)
  * `fed_rate`: float (range: `0.0` to `10.0`, default: `5.25`)
  * `geopolitical_risk`: float (range: `0.0` to `100.0`, default: `40.0`)
* **Output (200 OK)**:
  ```json
  {
    "inputs": {
      "oil_price": 100.0,
      "fed_rate": 5.25,
      "geopolitical_risk": 40.0
    },
    "metrics": {
      "cpi_inflation": {
        "value": 5.46,
        "baseline": 4.85,
        "change": 0.61,
        "status": "Rising Inflation"
      }
      // usd_inr, rbi_repo_rate, gdp_growth, nifty_50
    },
    "sectors": [
      {
        "name": "Aviation",
        "score": -61,
        "impact": "Hurt",
        "driver": "Fuel cost pressure"
      }
    ]
  }
  ```

#### 4. AI Analyst Copilot
* **Route**: `GET /api/ai/ask`
* **Purpose**: Answers natural language economic queries.
* **Query Parameters**:
  * `query`: string (non-empty)
* **Output (200 OK)**:
  ```json
  {
    "engine": "Local Narrative engine (Fallback)",
    "query": "Why is gold rising?",
    "title": "Why is Gold Rising?",
    "summary": "Gold has surged due to growing expectations of interest rate cuts by the US Federal Reserve...",
    "cause": "US Dollar weakening, declining US Treasury bond yields, central bank buying...",
    "effect": "Gold prices hit record highs, surpassing $2,400 per ounce. Dollar index drops.",
    "india_impact": [
      "Import Bill Surges: Since India imports most of its gold, jewelry raw cost rises..."
    ],
    "details": {
      "root_cause": "A structural shift in global reserves...",
      "risks": "Prolonged high prices might squeeze consumer demand...",
      "opportunities": "Gold loan NBFCs benefit from higher collateral...",
      "historical_comparison": "Similar to the 1970s stagflation...",
      "predictions": "Gold is projected to find strong support and breach $2600..."
    }
  }
  ```

#### 5. Relationship Graph
* **Route**: `GET /api/ai/relationship/graph`
* **Purpose**: Returns nodes and edges mapping the macro knowledge graph.
* **Output (200 OK)**:
  ```json
  {
    "nodes": [
      {
        "id": "oil",
        "label": "Crude Oil Price",
        "category": "Commodity",
        "description": "Global price of Brent and WTI crude oil..."
      }
    ],
    "links": [
      {
        "source": "oil",
        "target": "usd_inr",
        "relationship": "India's massive oil imports require purchasing more dollars, weakening the rupee.",
        "sign": "+"
      }
    ]
  }
  ```

#### 6. Causality Pathway
* **Route**: `GET /api/ai/relationship/causality`
* **Purpose**: Computes the shortest causal pathway between a source and a target.
* **Query Parameters**:
  * `source`: string (node ID, e.g. `oil`)
  * `target`: string (node ID, e.g. `stock_market`)
* **Output (200 OK)**:
  ```json
  [
    {
      "step": 1,
      "source": "Crude Oil Price",
      "target": "Corporate Profit Margins",
      "relationship": "Raises input chemical/fuel costs, compressing corporate profit margins.",
      "sign": "-"
    },
    {
      "step": 2,
      "source": "Corporate Profit Margins",
      "target": "Indian Equity Market",
      "relationship": "Falling corporate earnings drive stock index valuations down.",
      "sign": "+"
    }
  ]
  ```

---

## 10. Database Design
There is **no persistent physical database** (such as PostgreSQL, MySQL, or MongoDB) configured in the codebase. All data structures are in-memory python structures or transient variables.

```
┌────────────────────────────────────────────────────────┐
│                   In-Memory Database                   │
├────────────────────────┬───────────────────────────────┤
│ File                   │ Data Structure                │
├────────────────────────┼───────────────────────────────┤
│ economic_data.py       │ ECONOMIC_INDICATORS (Dict)    │
│ market_data.py         │ _cache (Dict), _cache_time    │
│ news_engine.py         │ SEED_NEWS (List of Dicts)     │
│ relationship_engine.py │ NODES (List), EDGES (List)    │
│ ai_analyst.py          │ SEMANTIC_ANSWERS (Dict)       │
└────────────────────────┴───────────────────────────────┘
```

* **Transient State**: Live Brownian ticks are generated dynamically inside the uvicorn thread loop and broadcast straight to WebSocket clients without database persistence.
* **Caching Duration**: `MarketDataService` implements a 5-minute cache time limit:
  `self.cache_duration_seconds = 300`
  If the delta between `now` and `self._cache_time` is less than 300 seconds, the service returns the cached JSON snapshot, avoiding `yfinance` API rate limits.

---

## 11. Frontend Architecture
The frontend is a single page application built on **Next.js 16 (App Router)** and **React 19**.

### Rendering & Styling
* **Vibrant Glassmorphic Aesthetics**: Styling is handled by PostCSS Tailwind v4. The global theme classes (`terminal-panel`, `glow-text-green`, `pulse-node`) use glassmorphism (translucent backgrounds with blur filters) to create a premium visual experience:
  ```css
  /* From frontend/src/app/globals.css */
  .terminal-panel {
    background: rgba(17, 24, 39, 0.45);
    border: 1px solid rgba(75, 85, 99, 0.25);
    backdrop-filter: blur(12px);
    border-radius: 4px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
  }
  ```
* **State Management**: State is centralized in the core page level (`page.tsx`) and passed down via props. 
  * `activeTab`: Tracks the active dashboard tab (`investor`, `economist`, `student`, `research`, `government`).
  * `liveTicks`: Tracks simulated tick frames received via WebSockets.
  * `alerts`: Tracks live alert notification history.
  * `isCommandBarOpen`: Controls the visibility of the global shortcut panel.
  * `copilotSearchQuery`: Links the command bar to the AI Analyst panel queries.

### Component Breakdown
1. **CommandBar**: Global Omnibox modal triggered with `Ctrl+K` or `/`. Lets users navigate dashboards, trigger simulations, or query the AI.
2. **MacroGraph**: Renders the macroeconomic causality graph on an SVG canvas using pre-defined coordinate scales.
3. **SimulatorPanel**: Renders three input ranges/sliders and outputs simulated macroeconomic metrics and sector progress bars.
4. **InvestorDashboard**: Displays a live-updating tickers table, custom SVG candlestick chart (OHLCV), and cross-asset correlation table.
5. **EconomistDashboard**: Renders baseline indicators and an AI forecasting trend chart with confidence bands.
6. **StudentDashboard**: Renders educational slides and interactive multiple-choice quizzes.
7. **ResearchDashboard**: Geopolitical timeline viewer with executive PDF report compilation simulation.
8. **GovernmentDashboard**: Table of port traffic and satellite night-light indices.

---

## 12. Backend Architecture
The backend is built as an asynchronous **FastAPI ASGI application**.

### Core Flow
* **Lifespan Manager**: Handles startup cache initialization.
* **Routing**: Endpoints are segmented into dedicated routers (`market`, `economy`, `news`, `scenario`, `ai`, `ws`) and registered in `app/main.py`.
* **Async Threading**: `yf.Ticker.history` and `yf.Ticker.fast_info` calls are blocking IO operations. To prevent them from blocking the async loop, the backend wraps them in `asyncio.get_event_loop().run_in_executor()` inside `MarketDataService`:
  ```python
  # From backend/app/services/market_data.py
  loop = asyncio.get_event_loop()
  info = await loop.run_in_executor(None, lambda: ticker_obj.fast_info)
  ```
* **Singletons**: All services are instantiated as singletons (`market_data_service = MarketDataService()`, etc.) and imported directly by routing files, maintaining a shared in-memory state.

---

## 13. AI/ML Pipeline & Forecasting Models
The platform models trends and queries using quantitative statistical models and qualitative language adapters.

### Quantitative Forecasting Models
The platform supports four forecasting models in `ForecastingService`:
1. **Prophet**: Additive regression model combining piecewise trends with seasonality.
2. **XGBoost**: Gradient Boosted Decision Trees utilizing lagged indicators.
3. **LSTM**: Recurrent neural network capturing sequential dependencies.
4. **Temporal Fusion Transformer**: Multi-horizon transformer combining self-attention with variable selection networks.

*Note: Since the codebase does not train active ML weights locally, these models return simulated time-series outputs (12-month historical and 12-month forecasted periods) with realistic statistical properties (e.g., compounding standard deviations for confidence intervals).*

```python
# From backend/app/services/forecasting.py
# Confidence interval spread expands over forecast horizon
ci_spread = volatility * (i ** 0.5) * 1.5
```

### Qualitative AI Copilot Pipeline
The AI Copilot uses a multi-tier resolution process:

```
[User Query]
     │
     ▼
[Check settings.GEMINI_API_KEY] ──(Configured)──► [Gemini-Pro HTTP Request] ──► [Structured JSON Response]
     │ (Absent or Failed)
     ▼
[Check settings.OPENAI_API_KEY] ──(Configured)──► [GPT-4-Turbo HTTP Request] ──► [Structured JSON Response]
     │ (Absent or Failed)
     ▼
[Check settings.USE_OLLAMA] ─────(Enabled)─────► [Local Ollama HTTP Request] ──► [Structured JSON Response]
     │ (Absent or Failed)
     ▼
[Regex Keyword Matcher] ────────(Matched)───────► [Return Seeded Semantic Answer]
     │ (No Matches)
     ▼
[Local Synthesis Engine] ────────────────────────► [Return Synthesized Answer Card]
```

---

## 14. Security Audit
An inspection of settings, routers, and configurations highlights several security characteristics:

1. **Permissive CORS Configuration**:
   The active FastAPI backend (`app/main.py`) allows cross-origin resource sharing specifically for React developer environments:
   ```python
   # From backend/app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
   *Audit*: This is secure for local developer builds. However, the dead code file `backend/main.py` has a wildcard setting (`allow_origins=["*"]`), which would be high-risk if exposed to production.
2. **Unvalidated Query Inputs**:
   The router `ai.py` exposes query strings directly to external APIs without input sanitization:
   ```python
   # From backend/app/routers/ai.py
   @router.get("/ask")
   async def ask_copilot(query: str = Query(..., description="...")):
       return await ai_analyst_service.ask_question(query)
   ```
   *Audit*: Risks of Prompt Injection. If external API keys (Gemini/OpenAI) are configured, a malicious query could attempt prompt injection (e.g., instructing the LLM to ignore preceding instructions and output unrelated data).
3. **No Rate Limiting**:
   No rate limiting is implemented on the API routes or the WebSocket connection.
   *Audit*: Exposure to Denial of Service (DoS) attacks. A client can establish hundreds of WebSocket connections, consuming memory and triggering rapid `yfinance` fetches that could lead to IP bans.
4. **Hardcoded API Keys in env**:
   API keys are loaded directly from local environment config `.env`.
   *Audit*: Care must be taken not to commit files containing active API keys to public version control systems.

---

## 15. Performance Review
* **yfinance Thread Wrapping**: Wrapping `yfinance` in `run_in_executor` avoids blocking the main ASGI event loop. This keeps typical API request latencies low (often <50ms for cached routes).
* **WebSocket Serialization overhead**: The tick simulation loop broadcasts JSON payloads every 1.5 seconds.
  ```python
  # From backend/app/routers/ws.py
  ticks = market_data_service.generate_simulated_ticks()
  if ticks:
      await websocket.send_text(json.dumps({"type": "tick", "data": ticks}))
  ```
  Since the payload is small (around 3-4KB) and the client pool is typically small, serialization overhead is minimal. However, as the client pool grows, broadcasting sequentially in a single loop could lead to connection bottlenecks.
* **Debounce Optimization**: The 200ms debounce on the frontend sliders prevents overloading the simulation endpoint during active user interaction.

---

## 16. Testing Assessment
* **Current Test Coverage**:
  * **API Integration Tests**: `/scripts/test_backend.py` validates that core endpoints respond with `200 OK` and contain expected keys.
  * **Ollama Verification**: `/backend/app/services/test_local_ollama.py` checks that local Ollama models return valid JSON schemas.
  * **Performance Benchmarking**: `/scripts/performance_benchmark.py` runs 20-run latency checks and measures WebSocket tick intervals and jitter.
* **Gaps**:
  * No unit tests (e.g., pytest) testing isolated service logic (such as regression formulas in `ScenarioSimulatorService` or deduplication rules in `NewsIntelligenceEngine`).
  * No frontend tests (such as Jest or Cypress) validating UI rendering or tab switching.
  * The integration tests require a running server on port 8000; they cannot be run in an isolated CI pipeline without manual orchestration.

---

## 17. DevOps Analysis
* **Docker/Containerization**: 
  * *Unable to verify from current repository.* No Dockerfiles or docker-compose configurations are present.
* **CI/CD Configuration**: 
  * *Unable to verify from current repository.* No GitHub Actions workflows or other CI/CD pipeline files are present.
* **Rollback & Scaling Strategy**:
  * *Unable to verify from current repository.* The application currently relies on local CLI startup commands (`npm run dev`, `uvicorn backend.app.main:app`).

---

## 18. Code Quality Review
* **Modularity**: Excellent. Separate modules handle config, services, and routers.
* **KISS & SOLID**: High adherence. Services represent single-responsibility singletons.
* **Naming Consistency**: High consistency. CamelCase is used in the frontend; snake_case is used in the backend.
* **Comments**: Crucial files are commented, explaining key mathematical coefficients and transmission channels.
* **DRY**: Some duplication of default pricing configurations exists between `market_data_service` and the test files, but core calculations remain DRY.

---

## 19. Design Patterns

### 1. Singleton Pattern
All services are instantiated as singletons at the bottom of their respective files and imported across routers:
* **Example**:
  ```python
  # In backend/app/services/market_data.py
  market_data_service = MarketDataService()
  ```

### 2. Strategy Pattern
The `ForecastingService` implements a strategy-like structure, selecting reasoning and parameters based on the requested model name:
* **Example**:
  ```python
  # In backend/app/services/forecasting.py
  reasons = {
      "Prophet": "...",
      "XGBoost": "...",
      "LSTM": "...",
      "Temporal Fusion Transformer": "..."
  }
  ```

### 3. Adapter / Router Pattern
The `AIAnalystService` acts as an adapter, translating a single `ask_question` call into API requests for Google Gemini, OpenAI, or local Ollama:
* **Example**:
  ```python
  # In backend/app/services/ai_analyst.py
  async def ask_question(self, query: str):
      # Resolves using _call_gemini_api or _call_openai_api or _call_ollama_api
  ```

### 4. Command Pattern
The frontend `CommandBar` maps natural language commands to specific application actions:
* **Example**:
  ```typescript
  // In frontend/src/app/page.tsx
  const executeCommand = (cmd: string) => {
    if (cmd.startsWith('/dashboard')) { ... }
    else if (cmd.startsWith('/simulate')) { ... }
  };
  ```

---

## 20. Strengths
1. **High-Performance Async Foundation**: Using FastAPI's async execution loop ensures minimal latencies and efficient concurrency.
2. **Resilient AI Fallback Pipeline**: The multi-tiered fallback architecture ensures the AI Copilot remains functional even without internet connectivity or API keys.
3. **Clean Decoupled Design**: The frontend handles presentation and layout, while the backend processes simulations and routes queries.
4. **Rich Aesthetic Design**: The dark-mode glassmorphic interface provides a polished, modern developer dashboard experience.

---

## 21. Weaknesses
1. **No Persistent Data Storage**: The application has no database. Restarts lose tick data, and alternative metrics are hardcoded.
2. **Hardcoded Coordinates in Graph**: The coordinates in `MacroGraph.tsx` are hardcoded. Adding new nodes requires manual layout changes.
3. **Lack of Rate Limiting**: The system is vulnerable to DoS attacks due to unrestricted API and WebSocket access.
4. **Permissive CORS Settings**: Wildcard configurations in prototype files present security risks if deployed to production.

---

## 22. Technical Debt
* **Obsolete Files**: `backend/services/oms.py` and `backend/main.py` are dead code.
* **Tracked Cache Files**: Python cache binaries (`.pyc` files) are tracked in the repository.
* **Hardcoded Regression Coefficients**: The econometric multipliers in `scenario_simulator.py` are hardcoded.

---

## 23. Risks
* **yfinance API Limits**: Frequent restarts or high traffic can cause `yfinance` to throttle requests.
* **LLM Token Costs**: If external APIs are enabled, heavy traffic could lead to high billing costs.
* **Prompt Injection**: Lack of input validation on `/api/ai/ask` routes could expose the system to prompt injection.

---

## 24. Improvement Roadmap

| Rank | Improvement | Difficulty | Risk | Target Time | Impact |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **1** | Clean dead code (`backend/services/oms.py`, old `main.py`) | Easy | Low | 1 hour | Medium |
| **2** | Add input sanitization and length validation to `/api/ai/ask` | Easy | Low | 2 hours | High (Security) |
| **3** | Integrate PostgreSQL / TimescaleDB for persistent tick logging | Medium | Medium | 2 days | High |
| **4** | Dynamic Force-Directed Layout for the Causal Macro Graph | Hard | Low | 3 days | High |
| **5** | Implement rate limiting (e.g., Slowapi) | Medium | Low | 1 day | High (Security) |

---

## 25. Glossary of Important Components
* **DXY (US Dollar Index)**: Measures the value of the US Dollar against a basket of foreign currencies.
* **CPI (Consumer Price Index)**: Tracks changes in the prices of consumer goods and services (retail inflation).
* **WPI (Wholesale Price Index)**: Measures price changes at the wholesale level.
* **FII (Foreign Institutional Investor)**: Institutional investment capital originating outside India.
* **TEU (Twenty-foot Equivalent Unit)**: Standard unit of measurement for container port traffic.
* **Brownian Walk**: Mathematical model representing random motion, used here to simulate price ticks.
* **Jaccard Headline Similarity**: Ratio of the intersection to the union of word tokens, used to deduplicate news headlines.

---

## 26. Complete Dependency Graph

```
                      [Next.js Client]
                             │
                             ├─► Lucide React (Icons)
                             ├─► Tailwind CSS (Style)
                             └─► React 19 (Hooks)
                                     │
                             (HTTP / Websockets)
                                     │
                             [FastAPI Backend]
                                     │
        ┌───────────────┬────────────┴───┬──────────────────┐
        ▼               ▼                ▼                  ▼
  [yfinance]        [Pandas]          [SciPy]            [Httpx]
 (Market data)  (Time-series Data)  (Regressions)   (LLM Connections)
        │               │                                   │
        └───────┬───────┘                                   ▼
                ▼                                      [LLM APIs]
             [NumPy]                              (Gemini, OpenAI, Ollama)
```

---

## 27. Complete Module Interaction Diagram
Below is a text-based map of system interactions:

```
[UI Dashboard Page]
   │
   ├── (1) Mounts ──► Requests `/api/market/snapshot` ──► Returns Cached Snap (FastAPI)
   │
   ├── (2) Connects ─► WebSocket `/api/ws` ──► Streams Brownian Price Ticks (FastAPI)
   │
   ├── (3) Adjusts Sliders ──► GET `/api/scenario/simulate` ──► Resolves Offsets (Scenario Engine)
   │
   ├── (4) Types Command ──► Triggers Omnibox Command Action (CommandBar)
   │
   └── (5) Asks Question ──► GET `/api/ai/ask` ──► Selects Engine (AI Analyst Service)
```

---

## 28. "How I Would Continue Developing This Project"
If assigned to lead this project, I would execute the following development sprints:

### Sprint 1: Code Sanitization & Dependency Locking
* Delete `backend/services/oms.py`, `backend/services/market_data.py`, and `backend/main.py`.
* Remove all `.pyc` files from the Git index and add `__pycache__/` to the root `.gitignore`.
* Create a lockfile (e.g., using `pip-tools` or Poetry) to lock dependency versions.

### Sprint 2: Persistent Database Integration
* Introduce a PostgreSQL database container.
* Add TimescaleDB extensions to store historical simulated ticks.
* Migrate pre-seeded alternative indices and historical economic indicators from static code arrays into SQL tables.

### Sprint 3: Advanced Charting & Force Graph Layout
* Replace the custom SVG charting component in `InvestorDashboard.tsx` with TradingView Lightweight Charts for interactive zooming and panning.
* Implement a force-directed simulation in D3.js or React Flow to layout nodes in `MacroGraph.tsx` dynamically, replacing the hardcoded coordinate arrays.

### Sprint 4: Security & Production Readiness
* Add input sanitization on all text routes.
* Implement rate-limiting middleware in FastAPI using Redis.
* Write a Dockerfile and docker-compose configuration for the backend, frontend, and database services.
