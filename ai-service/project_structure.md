# PantryPulse & OpenClaw Project Structure & Architecture

This document describes the design patterns, architectural layers, and implementation details of the GenAI features, Hybrid Routing System, and OpenClaw orchestration engine.

---

## Project Directory Structure

```
ai-service/
├── app/                      # FastAPI Backend Microservice
│   ├── api/                  # REST Controllers & Proxy Routes
│   │   ├── chat.py           # POST /chat endpoint (Triggers HybridChatService)
│   │   ├── spring_proxy.py   # Proxy routes forwarding to Spring Boot endpoints
│   │   ├── optimization.py   # POST /optimization endpoint
│   │   ├── recipe.py         # POST /recipe endpoint
│   │   ├── menu.py           # POST /menu endpoint
│   │   ├── pricing.py        # POST /pricing endpoint
│   │   ├── description.py    # POST /description endpoint
│   │   └── supplier.py       # POST /supplier endpoint (AI Procurement Assistant)
│   ├── core/                 # Environment, Config & Global Settings
│   ├── knowledge/            # Static BOH Knowledge Database (JSON)
│   │   ├── recipes.json      # Master recipe dataset (9,132+ unique recipes)
│   │   ├── safety.json       # 45 BOH kitchen safety & first-aid protocols
│   │   ├── seasonal.json     # 12 traditional Telugu lunar months calendar & festivals
│   │   ├── pairing.json      # Regional dish pairing guidelines
│   │   ├── chef_notes.json   # Back-of-house culinary prep guidelines
│   │   └── suppliers.json    # Commercial vendors & LPG gas directory
│   ├── llm/                  # Multi-provider manager, retry, and health modules
│   │   ├── provider_manager.py # Primary/Fallback provider failover execution
│   │   ├── openrouter_client.py# OpenRouter Llama 3.1 Gateway client
│   │   └── providers/        # Individual API provider adapters (Gemini, OpenRouter, DeepSeek, Mistral)
│   ├── models/               # Pydantic schemas, Route/Intent Data Models
│   ├── prompts/              # System & Tool Prompt Sheets
│   │   ├── prompt_builder.py # System Prompt & Current System Date Injector
│   │   └── supplier_prompt.py# Corporate Procurement Request Email Prompt
│   ├── rag/                  # Retriever & Embeddings Engine
│   ├── retrievers/           # Base, FAISS, and Pinecone Cloud query retriever implementations
│   ├── routing/              # Query Intent Detection & Decision Router (Phase 2)
│   │   └── intent_router.py  # Intent Classifier & Lazy Anchor Embedding Loader
│   ├── schemas/              # Pydantic Request & Response Validators
│   └── services/             # Core AI Services & Integration Layer
│       ├── hybrid_chat_service.py # Hybrid Orchestrator & Telemetry Timer ([TIMING 1]-[TIMING 4])
│       ├── context_builder.py     # Unified Context Aggregator (Spring Boot + Pinecone RAG)
│       ├── supplier_service.py    # Corporate AI Procurement Email Generator
│       ├── spring_api.py         # Spring Boot REST Microservice Client
│       └── chatbot_service.py    # Singleton Chatbot Engine Handle
├── vector_db/                # Local FAISS Database Store Backup
├── openclaw/                 # OpenClaw Workflow Engine
│   ├── api/                  # Main /orchestrate entry point route
│   ├── config/               # Default Orchestrator configs
│   ├── integration/          # Dashboard, Menu, Supplier, & Reports publishers
│   ├── models/               # Mirrored OpenClaw response schemas
│   ├── operations/           # Print Queue, execution logs, status tracker
│   ├── routes/               # Dispatcher hooks & completion checks
│   ├── services/             # HTTP Client gateway wrappers
│   └── workflows/            # Restaurant sequential execution flow
├── scripts/                  # Vector DB sync & embedding population scripts
└── tests/                    # Unit verification test suites
```

---

## Implemented GenAI Features & Hybrid Architecture Systems

The system implements 8 advanced AI features integrated into a high-speed Hybrid Architecture:

### 1. Hybrid Multilingual Chatbot & Intent Routing Engine

* **Phase 2 Intent Router**: Classifies incoming queries into 9 Intent categories (`INVENTORY`, `RECIPE`, `SUPPLIER`, `PRICING`, `EXPIRATION`, `DASHBOARD`, `KNOWLEDGE`, `GENERAL_CHAT`, `SETTINGS`) and dispatches across 4 execution routes (`SPRING_*`, `PINECONE`, `HYBRID`, `GEMINI_ONLY`).
* **High-Speed Singleton Caching**: Uses in-memory Singleton handles for `ChatbotService` and `IntentRouter` to avoid per-request re-initialization.
* **Lazy Anchor Query Embeddings**: Anchor query embeddings are computed lazily on-demand, ensuring Uvicorn binds port 8080 immediately (**0.1s container startup**) and eliminating HTTP 502 connection refusal errors on Railway deployments.
* **Sub-Second Latency (0.82s)**: Four-stage telemetry logging (`[TIMING 1]` to `[TIMING 4]`) tracks controller, service, context aggregator, and background execution.

### 2. Live Expiration & Multi-Source Inventory Tracking

* Concurrently gathers live inventory stock (`/api/inventory`) and expiration alerts (`/api/expiration/expiring`) from Spring Boot.
* Injects `Current System Date` into the system prompt and compares ingredient expiry dates against system date to accurately catch items expiring today (e.g. `mango` on `Jul 26, 2026`).

### 3. Corporate AI Procurement Assistant (Supplier Purchase Requests)

* Generates formal, highly professional procurement purchase request emails for low-stock ingredients using the Combined Corporate Email Format.
* Formats polite greetings, structured bullet-point details table (`• Ingredient`, `• Quantity`, `• Priority`, `• Required Before`), operational availability inquiries, Procurement Team signature, and AI Procurement Assistant footer.

### 4. Clean Text Presentation & Post-Processing

* Automatically strips internal technical terms ("knowledge base", "Pinecone", "RAG context", "database") to maintain confidentiality.
* Employs post-processing `clean_chat_formatting()` regex filters to transform messy Markdown asterisks (`* **Item:**`) into clean, elegant bullet points (`• Item:`).

### 5. Resilient Multi-Provider Fallback Gateway

* Prioritizes Google Gemini (`gemini-1.5-flash`) with automatic failover to OpenRouter Gateway (`meta-llama/llama-3.1-8b-instruct`), DeepSeek, Mistral, and RAG-only fallback.

### 6. Intelligent Inventory Optimization

* Exposes `POST /optimization` to calculate food waste prevented and estimated revenue margins. Overrides priority to `HIGH` for short-expiry items (1-2 days).

### 7. Smart Recipe Recommendations & Menu Specials Planner

* Validates available ingredients against live inventory and Pinecone RAG, prioritizing short-expiry items and highest estimated profit margins.

### 8. AI Pricing Suggestions & Culinary Menu Descriptions

* Classifies pricing strategies (Premium/Standard/Value) and market positioning based on estimated gross profit percentages. Scrubs metadata to craft customer-ready menu copy.

---

## OpenClaw Orchestration Architecture

The **OpenClaw Orchestrator** functions as a supervisor coordinating independent FastAPI microservices into a unified pipeline:

```
[Inventory updates] 
        ↓
[OpenClaw Workflow Manager]
        ↓
[Restaurant Sequential Workflow] 
  ├── 1. Optimization ────→ (Extracts used ingredients & purchase alerts)
  ├── 2. Recipe ──────────→ (Recommends recipes based on optimized usage)
  ├── 3. Menu Specials ───→ (Aligns daily specials with chosen recipes)
  ├── 4. Pricing ─────────→ (Sets strategy, position, and confidence)
  ├── 5. Description ─────→ (Scrubs copy and styles tone)
  └── 6. Supplier ────────→ (Drafts orders ONLY when purchase_required=True)
        ↓
[Workflow Publisher & Dispatcher]
  ├── Dashboard adapter  ──→ (Waste summary, recommended recipes list)
  ├── Menu adapter       ──→ (Special menu list, selling prices)
  ├── Supplier adapter   ──→ (Replenishment corporate procurement emails)
  └── Reports adapter    ──→ (Financial summary, ISO 8601 timestamps)
        ↓
[Operational Completion Manager]
  ├── Print Queue ────────→ (Simulated print queue list & ISO job details)
  ├── Lifecycle Tracker ──→ (PENDING -> RUNNING -> COMPLETED status log)
  └── Execution Logger ───→ (Records step execution times & warning arrays)
```

---

* For quick run instructions, see [README.md](file:///e:/TCWING_PRJ/ai-service/README.md).
* For directory logic details, see [Project_logic_explanation.md](file:///e:/TCWING_PRJ/ai-service/Project_logic_explanation.md).
