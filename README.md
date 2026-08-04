# OpenTerminal (The Hummingbird Project)

> **A Modular, Agent-Driven Economic Intelligence Operating System (EIOS)**

## Overview
OpenTerminal is an open-source financial operating system and desktop workstation. Designed to model the core user experience of institutional trading systems (such as Bloomberg or Reuters Eikon), it translates complex global economic shocks into domestic transmission channels affecting the Indian economy and financial markets in real time.

EIOS evolves OpenTerminal from a client-server single-page dashboard into a fully decoupled, event-driven, multi-database, plugin-based operating system powered by autonomous AI Agent Swarms.

---

## Problem
Retail investors, financial analysts, and economics students frequently struggle to comprehend the complex, multi-layered transmission pathways through which global macroeconomic shifts propagate into domestic markets. Traditional financial software is either gatekept by exorbitant subscription fees ($24,000+/year) or presents data in isolation without visualizing or simulating causal relationships between global triggers (such as Brent Crude spikes, US Federal Reserve rate hikes, or geopolitical escalation) and domestic transmission channels (USD/INR exchange rates, CPI inflation, RBI repo rates, GDP growth, and equity valuations).

---

## Solution
OpenTerminal bridges this gap by providing an open-source institutional financial workstation featuring:
1. **Macroeconomic Transmission Modeling**: Simulates the Commodity Price Channel, Interest Rate Differential Channel, and Safe-Haven Asset Channel dynamically.
2. **Interactive Scenario Simulator**: Enables real-time stress testing of macro parameters (Crude prices, Fed rates, Geopolitical Risk Index) with instant offset calculations.
3. **Causality Graph Engine**: Traces the shortest propagation pathways between economic variables using interactive node-link network graphs.
4. **Resilient AI Copilot Swarm**: Delivers institutional narrative reports leveraging a multi-tier fallback architecture (Google Gemini ➔ OpenAI GPT-4 ➔ Local Ollama ➔ Offline Rule-Based Semantic Templates).
5. **Event-Driven Plugin System**: A modular micro-kernel architecture where every feature is an independent plugin module auto-discovered at runtime.
6. **Provider-Agnostic Data Adapters**: Unified ports decoupling data ingestion across Yahoo Finance, FRED, World Bank, RBI, RSS news feeds, and local CSV files.

---

## EIOS Architecture & System Design

```
                               ┌─────────────────────────────────────────────────────────┐
                               │                    PRESENTATION LAYER                   │
                               │  (Next.js 16 Client / CLI / External API Consumers)     │
                               └────────────────────────────┬────────────────────────────┘
                                                            │ REST / WebSockets / SSE
                                                            ▼
                               ┌─────────────────────────────────────────────────────────┐
                               │                    API GATEWAY & ROUTER                 │
                               │          (Dynamic Module Route & WS Discovery)          │
                               └────────────────────────────┬────────────────────────────┘
                                                            │ Task Dispatch
                                                            ▼
                               ┌─────────────────────────────────────────────────────────┐
                               │                   SUPERVISOR AGENT                      │
                               │     (Planner, Router, Memory, Reasoning, Aggregator)    │
                               └──────────────┬───────────────────────────▲──────────────┘
                                              │ Publish Task              │ Return Synthesis
                                              ▼                           │
 ┌────────────────────────────────────────────────────────────────────────┴────────────────────────────────────────────────────────┐
 │                                                      EVENT BUS (Pub/Sub)                                                        │
 └──────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬───────┘
        │ Raw News             │ Indicator Shift      │ Forecast Req         │ Causal Path Req      │ Risk Assessment      │ Alert
        ▼                      ▼                      ▼                      ▼                      ▼                      ▼
 ┌──────────────┐       ┌──────────────┐       ┌──────────────┐       ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
 │  News Agent  │       │  Macro Agent │       │Forecast Agent│       │ Graph Agent  │       │  Risk Agent  │       │ Alert Agent  │
 └──────┬───────┘       └──────┬───────┘       └──────┬───────┘       └──────┬───────┘       └──────┬───────┘       └──────┬───────┘
        │                      │                      │                      │                      │                      │
 ┌──────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴───────┐
 │                                                UNIFIED DATA & REPOSITORY LAYER                                                  │
 └──────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬───────┘
        │ PostgreSQL           │ TimescaleDB          │ Neo4j                │ Qdrant               │ Redis                │ Adapters
        ▼                      ▼                      ▼                      ▼                      ▼                      ▼
 ┌──────────────┐       ┌──────────────┐       ┌──────────────┐       ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
 │ Relational DB│       │ Time-Series  │       │ Knowledge    │       │ Vector Store │       │ Cache/Queue  │       │ Data Source  │
 │ (Users/Logs) │       │ (Ticks/Macro)│       │ (Causality)  │       │ (Embeddings) │       │ (Pub/Sub)    │       │ Adapters     │
 └──────────────┘       └──────────────┘       └──────────────┘       └──────────────┘       └──────────────┘       └──────────────┘
```

### Key Architectural Principles
* **Hexagonal Architecture (Ports and Adapters)**: Core domain logic is completely isolated from external dependencies. Data sources implement `IDataAdapter`; storage engines implement `IRepository`.
* **Dynamic Plugin System**: Features are packaged into self-contained plugin modules inside `backend/app/modules/` implementing `BaseModule` / `IPluginModule`. The boot loader (`bootstrap_modules`) dynamically discovers, initializes, and mounts routes without modifying core files.
* **Event-Driven Pub/Sub**: Autonomous background agents communicate strictly via asynchronous domain events published onto the `EventBroker` (AsyncIO / Redis Pub/Sub).
* **Dependency Injection Container**: A central `DependencyContainer` handles singleton resolution for event brokers, data adapters, and repository ports.

---

## Core Features

### 1. Multi-Role Glassmorphic Dashboard
Five desktop panels tailored for financial roles:
* **Investor**: Real-time ticker feeds, custom SVG candlestick charts, and cross-asset correlation matrices.
* **Economist**: Baseline macroeconomic indicators, interactive shock stress-test simulator, and AI forecasting trends with confidence intervals.
* **Student**: Educational lesson modules and interactive macroeconomics quizzes.
* **Research**: Geopolitical shock timelines and automated executive PDF report compiler.
* **Government**: High-frequency alternative data tracking container port traffic and satellite night-light indices.

### 2. Scenario Stress-Test Simulator
Adjust parameters (Brent Crude, US Fed interest rate, Geopolitical Risk Index) via interactive sliders to observe instant simulated transmission impacts on CPI inflation, USD/INR exchange rates, RBI repo rate, GDP growth, and sector sensitivity indices.

### 3. Macroeconomic Causality Network Graph
An interactive SVG node-link visualization mapping variables (Crude Oil, Rupee, Corporate Profit Margins, Equity Multiples). Computes and highlights the shortest causal transmission paths between any two economic nodes.

### 4. Omnibox Command Bar
A global keyboard shortcut palette (`Ctrl+K` or `/`) allowing instant navigation between dashboards, scenario execution, and natural-language AI Analyst queries.

---

## Tech Stack

### Frontend Client
* **Framework**: React 19, Next.js 16 (App Router), TypeScript
* **Styling**: Tailwind CSS v4, Glassmorphic CSS custom properties
* **Icons**: Lucide React
* **State & Networking**: WebSockets streaming client, React Context

### Backend Engine
* **Language/Framework**: Python 3.9+, FastAPI, Uvicorn (ASGI Server)
* **Architecture**: Domain-Driven Design (DDD), Hexagonal Architecture, Event-Driven Pub/Sub
* **Data Adapters**: Yahoo Finance (`yfinance`), FRED API, World Bank Open Data, RBI Data, RSS Feed Scraper, CSV Importer
* **Math & Analytics**: NumPy, Pandas, SciPy (Brownian motion simulations and regression modeling)
* **AI Orchestration**: Google Gemini Pro API, OpenAI GPT-4 API, Local Ollama (Llama 3.2), Rule-based Semantic Template Engine

---

## Data Provider Adapters Layer

EIOS includes 6 provider-agnostic data adapters implementing the `IDataAdapter` interface:

| Adapter | Source | Indicators / Metrics | Fallback Strategy |
| :--- | :--- | :--- | :--- |
| **`YFinanceAdapter`** | Yahoo Finance | Equities indices (`^NSEI`, `^GSPC`), commodities (`GC=F`, `BZ=F`), forex (`INR=X`) | Offline price matrix seed |
| **`FREDAdapter`** | Federal Reserve Data | US Fed Funds Rate (`FEDFUNDS`), US CPI (`CPIAUCSL`), 10Y Yields (`GS10`) | Static macroeconomic seed series |
| **`WorldBankAdapter`** | World Bank Open Data | India Annual GDP Growth (`NY.GDP.MKTP.KD.ZG`), CPI Inflation, Trade % of GDP | Structural annual series seed |
| **`RBIAdapter`** | Reserve Bank of India | Repo Rate (`RBI_REPO`), Reverse Repo, CRR, SLR, Forex Reserves | Policy decision baseline seed |
| **`RSSAdapter`** | Financial News RSS Feeds | RSS News articles, Monetary Policy releases, Energy announcements | Pre-seeded financial news feed |
| **`CSVAdapter`** | Local Files | Proprietary offline time-series datasets (`data/*.csv`) | Synthetic time-series generator |

---

## Project Structure

```bash
OpenTerminal/
├── backend/
│   ├── app/
│   │   ├── adapters/                       # Data Provider Ingestion Adapters (Phase 2)
│   │   │   ├── base.py                     # IDataAdapter abstract interface
│   │   │   ├── yfinance_adapter.py         # Yahoo Finance market data adapter
│   │   │   ├── fred_adapter.py             # FRED US macroeconomic data adapter
│   │   │   ├── worldbank_adapter.py        # World Bank global indicators adapter
│   │   │   ├── rbi_adapter.py              # Reserve Bank of India policy rate adapter
│   │   │   ├── rss_adapter.py              # Financial news RSS feed adapter
│   │   │   └── csv_adapter.py              # Local CSV bulk dataset adapter
│   │   ├── core/                           # EIOS Kernel Infrastructure (Phase 1)
│   │   │   ├── boot.py                     # Dynamic plugin package auto-discovery loader
│   │   │   ├── config.py                   # Pydantic environment configuration
│   │   │   ├── container.py                # Pure DI Container instance & bindings
│   │   │   ├── event_bus.py                # AsyncIO / Pydantic BaseEvent bus
│   │   │   └── verify_phase1.py            # Core framework verification script
│   │   ├── modules/                        # Dynamic Feature Plugin Packages
│   │   │   ├── base.py                     # BaseModule plugin lifecycle contract
│   │   │   └── test_mock/                  # Framework verification test module
│   │   ├── routers/                        # REST & WebSocket API routers
│   │   ├── services/                       # Legacy core services (Refactored to adapters)
│   │   └── main.py                         # FastAPI App startup & lifespan coordinator
│   └── tests/                              # Automated Unit & Integration Test Suites
│       └── test_adapters.py                # Data Adapters unit test suite
│
├── frontend/                               # Next.js SPA Visual Terminal Client
│   ├── src/
│   │   ├── app/                            # Next.js App Router pages & styling
│   │   └── components/                     # Dashboard widgets & AI Copilot panels
│   └── package.json
│
├── doc/                                    # Architectural Documentation & Blueprints
│   ├── architectural_analysis.md           # Reverse engineering analysis report
│   ├── agent_terminal_blueprint.md         # Initial agent terminal specification
│   └── eios_architectural_blueprint.md     # Master EIOS architectural specification
└── README.md
```

---

## Installation & Setup

### Prerequisites
* **Python**: `3.9` or higher
* **Node.js**: `18.x` or higher
* **Package Managers**: `pip` and `npm`

### 1. Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. *(Optional)* Configure environment credentials in `backend/.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   USE_OLLAMA=false
   ```

### 2. Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd ../frontend
   ```
2. Install Node package dependencies:
   ```bash
   npm install
   ```

---

## Usage

### Running the Backend Server
From the `backend/` directory:
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive OpenAPI documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Running the Frontend Terminal Client
From the `frontend/` directory:
```bash
npm run dev
```
Access the workstation UI at [http://localhost:3000](http://localhost:3000).

### Running Automated Verification Test Suites
Run the Data Adapters unit test suite:
```bash
python -m unittest backend/tests/test_adapters.py
```

Run the Core Framework dynamic boot loader & event bus verification:
```bash
python -m backend.app.core.verify_phase1
```

---

## License
This project is licensed under the **MIT License**. See the [LICENSE](file:///c:/Users/shiva/OneDrive/Desktop/projects/OpenTerminal/LICENSE) file for details.
