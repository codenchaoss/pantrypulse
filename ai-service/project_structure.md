# KitchenSync & OpenClaw Project Structure & Architecture

This document describes the design patterns, architectural layers, and implementation details of the GenAI features and the OpenClaw orchestration system.

---

## Project Directory Structure

```
ai-service/
├── app/                      # FastAPI Backend
│   ├── api/                  # REST Controllers & Routes
│   ├── core/                 # Environment & Config
│   ├── knowledge/            # Static Culinary Database (JSON)
│   ├── llm/                  # Multi-provider manager, retry, and health modules
│   │   └── providers/        # Individual API provider clients (Gemini, Grok, OpenRouter, Together, Fireworks, DeepSeek, Mistral)
│   ├── prompts/              # System & Tool Prompt Sheets
│   ├── rag/                  # FAISS Retriever & Embeddings Builder
│   ├── retrievers/           # Base, FAISS, and Pinecone query retriever implementations
│   ├── schemas/              # Pydantic Request & Response Validators
│   └── services/             # Core AI Business Logic Services
├── vector_db/                # Local FAISS Database Store
├── openclaw/                 # OpenClaw Workflow Engine
│   ├── api/                  # Main /orchestrate entry point route
│   ├── config/               # Default Orchestrator configs
│   ├── integration/          # Dashboard, Menu, Supplier, & Reports publishers
│   ├── models/               # Mirrored OpenClaw response schemas
│   ├── operations/           # Print Queue, execution logs, status tracker
│   ├── routes/               # Dispatcher hooks & completion checks
│   ├── services/             # HTTP Client gateway wrappers
│   └── workflows/            # Restaurant sequential execution flow
├── scripts/                  # Embeddings population scripts
└── tests/                    # Unit verification tests suites
```

---

## Implemented GenAI Features

The system implements 8 advanced AI features designed to optimize back-of-house (BOH) operations:

### 1. Hybrid Multilingual Chatbot & BOH Safety Assistant

* Uses hybrid semantic vector searches (FAISS L2 distance) combined with fallback exact keyword indexing.
* Employs regex word-boundary tokenization (`re.findall(r'\b[a-z]+\b')`) to accurately detect language (English, Telugu, Tenglish) without false positives.
* Includes 45 master BOH kitchen safety, injury first-aid (Pasupu / turmeric on chopping cuts), and emergency protocols (`safety.json`).
* Integrates sub-seasons and 12 traditional Telugu lunar months calendar (`seasonal.json`) with festival menu recommendations.
* Handles casual BOH staff equipment layout queries (knives, aprons, towels, trash bins, clean plates, cutting boards, keys).

### 2. Intelligent Inventory Optimization

* Exposes `POST /optimization` to calculate food waste prevented and estimated revenue margins.
* Identifies low-stock conditions and generates replenishment package lists dynamically.
* Overrides priority to `HIGH` for short-expiry items (1-2 days).

### 3. Smart Recipe Recommendations

* Validates available ingredients against FAISS and scores compatibility with matched/missing ingredients metrics.
* Leverages master recipe datasets featuring Andhra Pradesh district specialties (Kakinada, Bhimavaram, Guntur, Rayalaseema, Nellore, Vizag), Telangana, Tamil Nadu, Kerala, Karnataka, Goa, Maharashtra, and Punjab dishes.

### 4. Daily Menu Specials Planner

* Structures and sorts proposed daily menu specials prioritizing short-expiry items (1-2 days), fewest missing ingredients, and highest estimated profit margins.

### 5. AI Pricing Suggestions

* Classifies pricing strategies (Premium/Standard/Value) and market positioning (Upscale/Mid-range/Budget) based on estimated gross profit percentages.

### 6. Clean Culinary Menu Descriptions

* Crafts customer-facing menu descriptions. Programmatically scrubs out scraped metadata or recipe website junk (e.g. blog headers).

### 7. Replenishment Supplier Messaging

* Generates drafted replenishment letters. Formats email subject lines, custom restaurant branding signatures, urgency indicators, commercial gas suppliers, and tracking order IDs (`KS-PR-XXXXX`).

### 8. Semantic RAG Search & Regional Pairings

* Exposes a semantic retriever interface to run raw queries over the vector database index.
* Features regional and seasonal dish pairings strictly adhering to master `{"ingredient": "...", "pairs": [...]}` schema (`pairing.json`).

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
  ├── Supplier adapter   ──→ (Replenishment review drafts)
  └── Reports adapter    ──→ (Financial summary, ISO 8601 timestamps)
        ↓
[Operational Completion Manager]
  ├── Print Queue ────────→ (Simulated print queue list & ISO job details)
  ├── Lifecycle Tracker ──→ (PENDING -> RUNNING -> COMPLETED status log)
  └── Execution Logger ───→ (Records step execution times & warning arrays)
```

---

* For quick run instructions, see the main Project README.md (README.md).
* For directory logic details, see the Project Logic Explanation (Project_logic_explanation.md).
