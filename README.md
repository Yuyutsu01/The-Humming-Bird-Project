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
4. **Autonomous AI Swarm Architecture**: Multi-agent cognitive network featuring a `SupervisorAgent` orchestrator and specialized worker agents (`NewsAgent`, `MacroAgent`, `ForecastAgent`, `GraphAgent`, `RiskAgent`).
5. **Resilient AI Copilot Swarm**: Delivers institutional narrative reports leveraging a multi-tier fallback architecture (Google Gemini ➔ OpenAI GPT-4 ➔ Local Ollama ➔ Offline Rule-Based Semantic Templates).
6. **Event-Driven Plugin System**: A modular micro-kernel architecture where every feature is an independent plugin module auto-discovered at runtime.
7. **Provider-Agnostic Data Adapters**: Unified ports decoupling data ingestion across Yahoo Finance, FRED, World Bank, RBI, RSS news feeds, and local CSV files.

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
 │                                                EVENT BROKER (Async Pub/Sub)                                                     │
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
* **Autonomous AI Swarm Engine**: High-level natural language prompts are parsed by the `SupervisorAgent`, which dynamically generates sub-tasks, dispatches them across topic channels (`agent.task.*`), and aggregates multi-agent intelligence.
* **Hexagonal Architecture (Ports and Adapters)**: Core domain logic is completely isolated from external dependencies. Data sources implement `IDataAdapter`; storage engines implement `IRepository`.
* **Dynamic Plugin System**: Features are packaged into self-contained plugin modules inside `backend/app/modules/` implementing `BaseModule`. The boot loader (`bootstrap_modules`) dynamically discovers, initializes, and mounts routes without modifying core files.
* **Event-Driven Pub/Sub**: Autonomous background agents communicate strictly via asynchronous domain events published onto the `EventBroker` (AsyncIO / Redis Pub/Sub).
* **Dependency Injection Container**: A central `DependencyContainer` handles singleton resolution for event brokers, data adapters, repository ports, and supervisor agents.

---

## Core Autonomous Swarm Agents

| Agent | Module Domain | Primary Responsibility | Event Topic Subscriptions |
| :--- | :--- | :--- | :--- |
| **`SupervisorAgent`** | Core Orchestrator | Natural language prompt intent parsing, task execution planning, and multi-agent synthesis | Gateway dispatcher |
| **`NewsAgent`** | `news` | RSS feed ingestion, headline token deduplication, and sentiment score analysis | `agent.task.news` |
| **`MacroAgent`** | `macro` | Transmission channel regressions (oil, Fed rate, geopolitics vs CPI & USD/INR) | `agent.task.macro` |
| **`ForecastAgent`** | `forecast` | Machine learning trend extrapolations and 12-month confidence interval projections | `agent.task.forecast` |
| **`GraphAgent`** | `knowledge_graph` | Macroeconomic causality network graph traversal and shortest path discovery | `agent.task.graph` |
| **`RiskAgent`** | `risk` | Corporate sector vulnerability scoring and equity exposure analysis | `agent.task.risk` |

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
│   │   ├── core/                           # EIOS Kernel Infrastructure (Phase 1 & 4)
│   │   │   ├── boot.py                     # Dynamic plugin package auto-discovery loader
│   │   │   ├── config.py                   # Pydantic environment configuration
│   │   │   ├── container.py                # Pure DI Container instance & bindings
│   │   │   ├── event_bus.py                # AsyncIO / Pydantic BaseEvent bus
│   │   │   ├── supervisor.py               # Autonomous AI Swarm Supervisor Agent
│   │   │   └── verify_phase1.py            # Core framework verification script
│   │   ├── modules/                        # Dynamic Feature Plugin Packages (Phase 3 & 4)
│   │   │   ├── forecast/                   # Forecasting plugin module & ForecastAgent
│   │   │   ├── knowledge_graph/            # Knowledge Graph plugin module & GraphAgent
│   │   │   ├── macro/                      # Macro Scenario plugin module & MacroAgent
│   │   │   ├── market/                     # Market Data & WebSockets plugin module
│   │   │   ├── news/                       # News Intelligence plugin module & NewsAgent
│   │   │   ├── risk/                       # Risk Analytics plugin module & RiskAgent
│   │   │   └── test_mock/                  # Framework verification test module
│   │   ├── repositories/                   # Storage Layer Repository Ports (Phase 3)
│   │   │   ├── base.py                     # IRepository abstract interface
│   │   │   ├── postgres_repo.py            # Relational PostgreSQL operational repository
│   │   │   ├── timeseries_repo.py          # Time-Series metrics repository
│   │   │   ├── graph_repo.py               # Neo4j knowledge graph repository
│   │   │   └── vector_repo.py              # Vector embeddings & RAG repository
│   │   └── main.py                         # FastAPI App startup & lifespan coordinator
│   └── tests/                              # Automated Unit & Integration Test Suites
│       ├── test_adapters.py                # Data Adapters unit test suite
│       ├── test_modules.py                 # Plugin Modules & Repositories test suite
│       └── test_agents.py                  # Swarm Agents & Supervisor test suite
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
Run the Swarm Agents unit test suite:
```bash
python -m unittest backend/tests/test_agents.py
```

Run the Plugin Modules unit test suite:
```bash
python -m unittest backend/tests/test_modules.py
```

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
