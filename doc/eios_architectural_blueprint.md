# Economic Intelligence Operating System (EIOS): System Blueprint & Architectural Redesign

---

## EXECUTIVE OVERVIEW

This document presents the complete reverse engineering analysis of the current OpenTerminal codebase and specifies the target **Economic Intelligence Operating System (EIOS)** architecture. 

EIOS evolves OpenTerminal from a client-server single-page dashboard into a production-grade, autonomous, agent-driven economic intelligence engine. The dashboard UI becomes merely one client of a decoupled, event-driven, multi-database, plugin-based operating system inspired by institutional terminals (Bloomberg) integrated with autonomous AI Agent Swarms.

---

# STEP 1 — EXISTING CODEBASE ANALYSIS REPORT

## 1. Existing Architecture Summary
The current codebase is a **Decoupled Client-Server Hybrid** with early Phase 1 foundational core abstractions:
* **Frontend**: Next.js 16 (App Router), React 19, TypeScript, PostCSS Tailwind CSS v4, Lucide React icons. Renders desktop dashboard panels (Investor, Economist, Student, Research, Government), an interactive SVG Macro Relationship Graph, a Scenario Stress-Test Simulator, an Omnibox Command Bar (`Ctrl+K`), and an AI Copilot chat drawer.
* **Backend**: FastAPI (Python 3.9+), Uvicorn ASGI server. Exposes REST endpoints (`/api/market`, `/api/economy`, `/api/news`, `/api/scenario`, `/api/ai`) and a WebSocket streaming endpoint (`/api/ws`).
* **Phase 1 Infrastructure**: Implements a `BaseModule` abstract lifecycle class (`initialize()`, `register_routes()`), an in-memory `AsyncIO` / Pydantic `BaseEvent` event broker, a `DependencyContainer` registry, and a dynamic module boot loader (`bootstrap_modules`) that auto-discovers plugins inside `backend/app/modules/`.

## 2. Codebase Strengths
1. **High-Performance Async Foundation**: Backend uses FastAPI's asynchronous event loop, running heavy synchronous operations (like `yfinance` fetches) inside thread pools (`run_in_executor`) to prevent loop blocking.
2. **Resilient Multi-Tier AI Routing**: The `AIAnalystService` features a robust 5-tier fallback cascade:
   `Google Gemini Pro` ➔ `OpenAI GPT-4` ➔ `Local Ollama (Llama 3.2)` ➔ `Rule-based Keyword Template Engine` ➔ `Generic Macro Synthesis Engine`.
3. **Glassmorphic Presentation**: High visual polish in the frontend using dark-mode glassmorphic styling (`terminal-panel`, `glow-text-green`, `pulse-node`).
4. **Clean Phase 1 Abstractions**: Core interfaces (`BaseModule`, `EventBroker`, `DependencyContainer`) provide a solid foundation for modular plugin extension.

## 3. Codebase Weaknesses
1. **Transient In-Memory State**: No physical database (PostgreSQL, Neo4j, Qdrant, or TimescaleDB) exists. All indicator series, news items, graph nodes, and market ticks reside in memory or static Python dictionaries. Restarts wipe dynamic state.
2. **Hardcoded Econometric Multipliers**: `ScenarioSimulatorService` uses hardcoded sensitivity coefficients (e.g. `0.08 * oil_diff`, `0.60 * fed_diff`).
3. **Static Node Coordinates**: `MacroGraph.tsx` relies on hardcoded SVG layout coordinates (`x: 50, y: 60`), preventing dynamic node additions.
4. **Lack of Background Worker System**: Long-running forecasts and news processing run directly inside API request threads instead of background queue workers (Celery/ARQ).

## 4. Tight Coupling Issues
1. **Backend Main Entrypoint**: `backend/app/main.py` explicitly imports legacy routers (`market`, `economy`, `ai`, `news`, `scenario`, `ws`) alongside the dynamic plugin loader `bootstrap_modules`.
2. **AI Service Dependency**: `AIAnalystService` directly imports `settings` from `backend.app.core.config` and static dictionaries from `SEMANTIC_ANSWERS`.
3. **Frontend Dashboard Nesting**: `page.tsx` tightly imports and renders dashboard components directly (`InvestorDashboard`, `EconomistDashboard`, etc.), rather than resolving widgets dynamically from a module UI registry.

## 5. Technical Debt
* **Tracked Cache Files**: Compiled Python bytecode (`.pyc` files under `backend/__pycache__/`) are tracked in Git.
* **Lack of Module Boundary Isolation**: Services in `backend/app/services/` are imported directly across different router handlers without clear domain boundary enforcement.
* **Missing DTO Contracts**: WebSocket messages use unstructured dictionaries rather than validated Pydantic/TypeScript DTO schemas.

## 6. Dead Code & Obsolete Files
* `backend/main.py`: Legacy root file importing non-existent `api.router` and `api.websocket`.
* `backend/services/oms.py`: Prototype Order Management System that is not imported or referenced anywhere in the application.
* `backend/services/market_data.py`: Obsolete single-quote prototype file superseded by `backend/app/services/market_data.py`.

## 7. Duplicate Logic
* **Ticker Defaults**: Default pricing dictionaries are duplicated between `market_data_service` and benchmark/test scripts (`performance_benchmark.py`).
* **Mock History Generators**: Time-series synthetic bar generation logic is duplicated between `market_data.py` and `forecasting.py`.

## 8. Missing Abstractions
* **Data Provider Abstraction**: No unified `IDataAdapter` exists. Data sources (`yfinance`, MoSPI, RBI data) are accessed through ad-hoc logic within specific service classes.
* **Repository Layer**: No `IRepository` abstraction exists to separate business logic from data access.
* **Supervisor Swarm Orchestrator**: No autonomous task planner exists to coordinate multi-agent reasoning over data events.

## 9. Scalability Issues
* **Serial WebSocket Broadcasting**: The tick broadcast loop sequentially iterates over all active WebSocket connections in a single thread loop.
* **Monolithic Memory Footprint**: Heavy operational state is stored in memory, blocking horizontal scaling across multiple application instances.
* **Absence of Rate Limiting & Caching Layer**: No Redis cache or API rate limiting is present.

## 10. Security Issues
* **Prompt Injection Risk**: `ai.py` exposes raw user strings directly to LLM prompts without input sanitization or structural validation.
* **Wildcard CORS Settings**: Legacy `backend/main.py` contains `allow_origins=["*"]`.
* **API Secret Management**: API keys rely on flat local `.env` files without secret vault integration or runtime key rotation.

---

# STEP 2 — TARGET ARCHITECTURE & SYSTEM DESIGN (EIOS)

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

## 1. Architecture Style
EIOS is built on **Domain-Driven Design (DDD)**, **Hexagonal Architecture (Ports and Adapters)**, **Plugin Architecture**, and **Event-Driven Architecture (EDA)**.

* **Domain-Driven Design**: The core system is partitioned into autonomous Bounded Contexts (Modules). Each domain owns its domain models, services, repositories, and handlers.
* **Hexagonal Architecture**: Business logic inside a module is decoupled from infrastructure details. Ports (Interfaces) define contract boundaries; Adapters implement connections to databases, messaging systems, and external web APIs.
* **Plugin Architecture**: Modules auto-register during boot. Adding or removing a feature requires zero modification to unrelated modules.
* **Event-Driven Architecture**: Components communicate strictly through asynchronous domain events published to an Event Bus broker.

## 2. Directory Structure

```
OpenTerminal/
├── backend/
│   ├── app/
│   │   ├── core/                           # EIOS Core Kernel Framework
│   │   │   ├── interfaces/                 # Global Interface Protocols
│   │   │   │   ├── adapter.py              # IDataAdapter protocol
│   │   │   │   ├── repository.py           # IRepository protocol
│   │   │   │   ├── event_bus.py            # IEventBus protocol
│   │   │   │   └── module.py               # IPluginModule protocol
│   │   │   ├── events/                     # Base Pydantic Event Schemas
│   │   │   │   ├── base.py                 # BaseEvent schema
│   │   │   │   └── domain_events.py        # System-wide core domain events
│   │   │   ├── container.py                # Pure DI Container Registry
│   │   │   ├── event_bus.py                # AsyncIO & Redis Event Bus implementations
│   │   │   ├── boot.py                     # Dynamic Module & Plugin Discovery Engine
│   │   │   ├── supervisor.py               # Autonomous AI Supervisor Agent
│   │   │   ├── scheduler.py                # Cron Scheduler & Periodic Job Manager
│   │   │   └── config.py                   # Pydantic Settings Manager
│   │   │
│   │   ├── domain/                         # Core Business Domain Entities
│   │   │   ├── models/                     # Shared Value Objects & Domain Schemas
│   │   │   └── exceptions.py               # Domain Exceptions
│   │   │
│   │   ├── adapters/                       # Data Provider Adapters (Ingestion Ports)
│   │   │   ├── base.py                     # Base Data Adapter Interface
│   │   │   ├── yfinance_adapter.py         # Yahoo Finance Data Ingest Adapter
│   │   │   ├── fred_adapter.py             # Federal Reserve Economic Data Adapter
│   │   │   ├── worldbank_adapter.py        # World Bank Indicators Adapter
│   │   │   ├── imf_adapter.py              # International Monetary Fund Adapter
│   │   │   ├── rbi_adapter.py              # Reserve Bank of India Data Adapter
│   │   │   ├── rss_adapter.py              # Financial News RSS Feed Adapter
│   │   │   └── csv_adapter.py              # Local CSV Bulk Import Adapter
│   │   │
│   │   ├── repositories/                   # Abstract Storage Repositories
│   │   │   ├── base.py                     # Generic Repository Interface
│   │   │   ├── postgres_repo.py            # Relational Storage Engine
│   │   │   ├── timeseries_repo.py          # Time-Series Storage Engine (TimescaleDB/Influx)
│   │   │   ├── graph_repo.py               # Graph Database Engine (Neo4j interface)
│   │   │   └── vector_repo.py              # Vector Embedding Engine (Qdrant interface)
│   │   │
│   │   ├── modules/                        # Autonomous Feature Plugins
│   │   │   ├── base.py                     # Module Base Protocol
│   │   │   │
│   │   │   ├── news/                       # News Intelligence Plugin Module
│   │   │   │   ├── domain/                 # Domain logic & sentiment analyzer
│   │   │   │   ├── agents/                 # Autonomous News Agent Service
│   │   │   │   ├── api/                    # REST / WS Endpoint Handlers
│   │   │   │   ├── models/                 # News Schemas & Pydantic DTOs
│   │   │   │   ├── workers/                # Deduplication & NLP Workers
│   │   │   │   ├── config.py               # Module-level Settings
│   │   │   │   └── registry.py             # Plugin Discovery Entrypoint
│   │   │   │
│   │   │   ├── macro/                      # Macroeconomic Sensitivity Plugin
│   │   │   ├── forecast/                   # Time-Series Forecasting Plugin
│   │   │   ├── knowledge_graph/            # Causal Relationship Graph Plugin
│   │   │   ├── risk/                       # Risk & Portfolio Analytics Plugin
│   │   │   ├── alerts/                     # Proactive Monitoring & Alert Plugin
│   │   │   ├── reports/                    # Executive Research Report Generator
│   │   │   └── test_mock/                  # Framework Verification Plugin
│   │   │
│   │   └── main.py                         # FastAPI Application Entrypoint
│   │
│   ├── scripts/                            # Dev & Benchmarking Scripts
│   ├── tests/                              # Unit, Integration, & Contract Test Suite
│   └── requirements.txt                    # System Dependencies
│
├── frontend/                               # Pure Presentation Client (Next.js 16)
│   ├── src/
│   │   ├── app/                            # Layout & Routing Shell
│   │   ├── components/
│   │   │   ├── core/                       # CommandBar, Header, Toast, Layout Shells
│   │   │   ├── widgets/                    # Dynamic Module Visualizers
│   │   │   └── dashboards/                 # Dashboard Layout Composers
│   │   └── registry/                       # UI Widget Auto-Registry
│   └── package.json
│
├── doc/                                    # System Documentation & Blueprints
├── docker-compose.yml                      # Local Multi-Container Infrastructure
└── README.md
```

## 3. Plugin Architecture & Discovery System
Modules auto-register during boot. A module is recognized as an EIOS plugin if it implements `IPluginModule`.

```python
# In backend/app/core/interfaces/module.py
from abc import ABC, abstractmethod
from fastapi import APIRouter
from typing import Dict, Any, List

class IPluginModule(ABC):
    """
    Standard Plugin Interface for all EIOS Feature Modules.
    """
    @property
    @abstractmethod
    def module_id(self) -> str:
        """Unique identifier for the module (e.g. 'news_intelligence')."""
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Initialize module resources, repositories, and DI container bindings."""
        pass

    @abstractmethod
    def register_routes(self) -> APIRouter:
        """Return the FastAPI APIRouter containing the module's HTTP/WS endpoints."""
        pass

    @abstractmethod
    def register_events(self) -> None:
        """Subscribe background agent event handlers to the central Event Bus."""
        pass

    @abstractmethod
    def register_workers(self) -> None:
        """Register asynchronous background queue workers (Celery/ARQ)."""
        pass

    @abstractmethod
    def get_health(self) -> Dict[str, Any]:
        """Return operational health status for the module."""
        pass
```

### Module Auto-Discovery Logic (`core/boot.py`)
```python
# In backend/app/core/boot.py
import importlib
import pkgutil
import logging
from fastapi import FastAPI, APIRouter
from backend.app.core.interfaces.module import IPluginModule

logger = logging.getLogger(__name__)

def bootstrap_modules(app: FastAPI) -> List[IPluginModule]:
    """
    Scans app.modules, dynamically imports registry.py from each subdirectory,
    instantiates IPluginModule subclasses, initializes resources, subscribes events,
    and mounts routers.
    """
    import backend.app.modules as modules_pkg
    loaded_modules: List[IPluginModule] = []
    
    for _, module_name, ispkg in pkgutil.iter_modules(modules_pkg.__path__):
        if not ispkg:
            continue
            
        try:
            reg_path = f"backend.app.modules.{module_name}.registry"
            reg_module = importlib.import_module(reg_path)
            
            for attr in dir(reg_module):
                cls = getattr(reg_module, attr)
                if (
                    isinstance(cls, type) 
                    and issubclass(cls, IPluginModule) 
                    and cls is not IPluginModule
                ):
                    instance: IPluginModule = cls()
                    instance.initialize()
                    instance.register_events()
                    instance.register_workers()
                    
                    router: APIRouter = instance.register_routes()
                    if router:
                        app.include_router(router)
                        
                    loaded_modules.append(instance)
                    logger.info(f"Loaded Plugin Module: [{instance.module_id}]")
                    break
        except Exception as e:
            logger.error(f"Failed to load module '{module_name}': {e}", exc_info=True)
            
    return loaded_modules
```

## 4. Event Bus Architecture & Event Schemas
Communication between modules occurs exclusively through events published to the `EventBroker`.

```
[Publisher Agent / Adapter] ──► EventBroker.publish("topic.name", event)
                                      │
                                      ├──► Subscriber 1 (News Agent)
                                      ├──► Subscriber 2 (Macro Agent)
                                      └──► Subscriber 3 (WebSockets Streaming)
```

### Base Event Schemas (`core/events/base.py`)
```python
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"
    source_module: str = Field(..., description="ID of module publishing the event")

class IndicatorUpdatedEvent(BaseEvent):
    indicator_name: str
    region: str
    current_value: float
    previous_value: float
    unit: str

class GeopoliticalShockEvent(BaseEvent):
    event_title: str
    risk_score_delta: float
    affected_commodities: list[str]

class MacroShiftCalculatedEvent(BaseEvent):
    oil_price: float
    fed_rate: float
    geopolitical_risk: float
    simulated_metrics: dict[str, float]
    sector_scores: list[dict[str, Any]]
```

## 5. Autonomous AI Agent Architecture (Supervisor & Workers)
The AI system uses a **Supervisor-Worker Swarm Pattern**.

```
                           ┌───────────────────────────┐
                           │      Supervisor Agent     │
                           │  - Parses User Intent     │
                           │  - Formulates Plan        │
                           │  - Evaluates Results      │
                           └─────────────┬─────────────┘
                                         │ Publishes Tasks
             ┌───────────────────────────┼───────────────────────────┐
             ▼                           ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
    │   News Agent    │         │   Macro Agent   │         │ Forecast Agent  │
    └─────────────────┘         └─────────────────┘         └─────────────────┘
```

### Supervisor Orchestrator Logic (`core/supervisor.py`)
```python
from typing import Dict, Any, List
import json
import logging
from backend.app.core.interfaces.event_bus import EventBroker
from backend.app.core.events.base import BaseEvent

logger = logging.getLogger(__name__)

class SupervisorAgent:
    """
    Cognitive Orchestrator. Evaluates inputs, formulates an execution plan,
    dispatches tasks via the Event Bus, and aggregates intelligence.
    """
    def __init__(self, event_bus: EventBroker, llm_provider):
        self.event_bus = event_bus
        self.llm = llm_provider

    async def orchestrate_query(self, user_query: str) -> Dict[str, Any]:
        # 1. Formulate Execution Plan
        plan = await self._plan(user_query)
        
        # 2. Dispatch events for target worker agents
        for task in plan.get("tasks", []):
            topic = f"agent.task.{task['agent_id']}"
            await self.event_bus.publish(topic, BaseEvent(source_module="supervisor"))
            
        # 3. Aggregate & Synthesize Outcomes
        synthesis = await self._synthesize(user_query, plan)
        return {
            "query": user_query,
            "plan": plan,
            "synthesis": synthesis
        }

    async def _plan(self, query: str) -> Dict[str, Any]:
        # Uses LLM to parse intent into structured agent execution graph
        return {"tasks": [{"agent_id": "news_agent"}, {"agent_id": "macro_agent"}]}

    async def _synthesize(self, query: str, plan: Dict[str, Any]) -> str:
        return "Synthesized macro intelligence report..."
```

## 6. Multi-Database Storage Architecture
EIOS decouples storage backends by mapping data models to optimized databases behind generic `IRepository` ports:

| Data Type | Storage Backend | Primary Responsibility | Repository Interface |
| :--- | :--- | :--- | :--- |
| **Relational Data** | **PostgreSQL** | User accounts, audit logs, system configurations, plugin states | `IPostgresRepository` |
| **Time-Series Ticks** | **TimescaleDB** | Real-time market ticks, historical economic indicator series | `ITimeSeriesRepository` |
| **Knowledge Graph** | **Neo4j** | Macroeconomic causality graph, transmission weights, node links | `IGraphRepository` |
| **Vector Embeddings** | **Qdrant** | News article embeddings, research papers, RAG semantic search | `IVectorRepository` |
| **Cache & Queues** | **Redis** | In-memory cache, rate limiting, pub/sub event bus, Celery broker | `ICacheRepository` |

### Repository Abstraction Protocol (`repositories/base.py`)
```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def list_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        pass

    @abstractmethod
    async def save(self, entity: T) -> T:
        pass

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        pass
```

## 7. Data Provider Adapters Layer
All external data fetching is handled through provider-agnostic adapters implementing `IDataAdapter`.

```python
# In backend/app/adapters/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class IDataAdapter(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the data provider (e.g. 'yfinance', 'FRED', 'WorldBank')."""
        pass

    @abstractmethod
    async def fetch_indicator(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Fetch normalized time-series data for a given indicator."""
        pass

    @abstractmethod
    async def get_health(self) -> bool:
        """Check provider connectivity status."""
        pass
```

### Concrete Adapters Included in EIOS Framework:
1. `YFinanceAdapter`: Stock market indices, commodities, forex rates.
2. `FREDAdapter`: Federal Reserve Economic Data (US interest rates, inflation).
3. `WorldBankAdapter`: Global GDP projections, trade balances.
4. `IMFAdapter`: International Monetary Fund outlooks.
5. `RBIAdapter`: Reserve Bank of India repo rates, forex reserves.
6. `RSSAdapter`: Financial news feed scrapers (Bloomberg RSS, Reuters RSS).
7. `CSVAdapter`: Offline bulk data import for custom economic series.

## 8. Background Processing & Distributed Workers
To ensure long-running AI generation, forecasting, and data ingestion do not block API endpoints, EIOS implements a distributed worker infrastructure using **Celery** backed by **Redis**.

```
[API / Event Bus] ──► Enqueue Task ──► [Redis Queue] ──► [Celery Worker Pool]
                                                               ├── News Deduplication Worker
                                                               ├── Forecast Calculation Worker
                                                               └── Report Generation Worker
```

### Scheduler & Periodic Jobs (`core/scheduler.py`)
Uses `APScheduler` or `Celery Beat` to trigger periodic background tasks:
* Every 1.5s: Perturb market tick cache (Brownian random walk simulation).
* Every 15m: Poll RSS feeds and deduplicate financial news.
* Every 6h: Refresh `yfinance` seeds and macro baseline indicators.

## 9. API Specifications

### REST Endpoints Summary
* `GET /api/v1/health`: Overall system health and plugin status.
* `GET /api/v1/market/snapshot`: Market data snapshot.
* `GET /api/v1/market/history`: Historical bar series.
* `GET /api/v1/economy/indicators`: Baseline domestic indicators.
* `GET /api/v1/scenario/simulate`: Macroeconomic shock simulation.
* `GET /api/v1/ai/ask`: AI Copilot query endpoint.
* `GET /api/v1/ai/relationship/graph`: Macro graph node/edge definitions.
* `GET /api/v1/news`: Processed news feed.

### WebSocket Streaming Specification
* **Endpoint**: `ws://localhost:8000/api/v1/ws`
* **Frames**:
  * `snapshot`: Initial market state payload upon client connection.
  * `tick`: Real-time streaming price tick updates (broadcast every 1.5s).
  * `alerts`: System notifications and threshold alerts.

## 10. Frontend Architecture (Pure Presentation Client)
The frontend is built on **Next.js 16 App Router** and **React 19**. It functions exclusively as a visualization client.

### Architectural Principles:
1. **Zero Business Logic**: All mathematical regressions, sentiment checks, and causality traces happen on the backend.
2. **Dynamic Widget Registry**: Dashboard panels render widgets from a registration map.
3. **WebSockets Event Listener**: Global `Home` page component manages a single WebSocket connection and distributes incoming ticks to child widgets via React context.

---

# MIGRATION PLAN & IMPLEMENTATION ROADMAP

## Phase-by-Phase Roadmap

### Phase 1: Core Framework Setup (COMPLETED)
* Created `BaseModule`, `EventBroker`, `DependencyContainer`, and `bootstrap_modules`.
* Verified dynamic route discovery and in-memory event dispatch via `verify_phase1.py`.

### Phase 2: Data Provider Adapters (CURRENT PHASE)
* Create `IDataAdapter` interface in `backend/app/adapters/base.py`.
* Implement `YFinanceAdapter`, `FREDAdapter`, `WorldBankAdapter`, `RBIAdapter`, `RSSAdapter`, `CSVAdapter`.
* Refactor `market_data.py` to consume `YFinanceAdapter`.
* Add unit tests for all adapters.

### Phase 3: Module Decoupling & Relational Repositories
* Extract `news`, `macro`, `forecast`, `knowledge_graph`, `risk`, `alerts`, `reports` into self-contained plugins under `backend/app/modules/`.
* Remove legacy router references from `backend/app/main.py`.
* Implement repository interfaces (`IPostgresRepository`, `ITimeSeriesRepository`, `IGraphRepository`, `IVectorRepository`).

### Phase 4: Autonomous Swarm Agent Layer
* Implement `SupervisorAgent` in `backend/app/core/supervisor.py`.
* Build specialized worker agents (`NewsAgent`, `MacroAgent`, `ForecastAgent`, `GraphAgent`, `RiskAgent`).
* Wire worker agents to listen on topic channels (`agent.task.*`).

### Phase 5: Distributed Background Workers & Scheduling
* Configure Celery task worker queues backed by Redis.
* Integrate APScheduler in `backend/app/core/scheduler.py` for periodic RSS polling and ticker updates.

### Phase 6: Production Hardening, Security & Observability
* Add input sanitization and prompt injection defenses to `/api/v1/ai/ask`.
* Implement rate limiting via `Slowapi` and Redis.
* Add Prometheus metrics endpoint (`/metrics`) and structured JSON logging.
* Clean up all legacy files (`backend/main.py`, `backend/services/`).

---

# NON-NEGOTIABLE EXECUTION RULES COMPLIANCE

1. **No Placeholder Code**: Every implementation must be fully functional and tested before progressing to the next step.
2. **Refactoring over Rewriting**: Existing code logic is preserved and refactored into the modular plugin structure.
3. **Phase Sign-Off Deliverables**: Each completed phase will output:
   * Architecture diagram
   * Dependency diagram
   * Detailed changelog
   * Performance impact assessment
   * Next recommended milestone
