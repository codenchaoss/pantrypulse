# PantryPulse: Hybrid AI Restaurant Management Platform

An enterprise AI-powered Back-of-House (BOH) restaurant management platform designed to automate and optimize kitchen operations. By combining a **Python FastAPI AI Microservice** with a **Java Spring Boot Enterprise Backend**, **Pinecone Cloud Vector RAG**, **Intent-Based Query Routing**, and the **OpenClaw Workflow Orchestrator**, PantryPulse analyzes live inventory stock, tracks ingredient expirations, predicts usage, recommends recipes, generates daily menu specials, optimizes food costing, drafts corporate supplier purchase requests, and coordinates execution across downstream printer and reporting modules.

---

## System Architecture Legend

To help trace data flows and system layers, the diagrams utilize the following color-coded categories:

* **Blue (AI Intelligence Modules)**: Cognitive AI reasoning microservices & LLM Provider Engine.
* **Green (Workflow & Orchestration)**: Lifecycle state trackers, Intent Router, and OpenClaw coordinators.
* **Orange (Spring Boot Enterprise APIs)**: Live inventory, recipe catalog, supplier directory, and dashboard endpoints.
* **Purple (Cloud Vector & Storage Outputs)**: Pinecone RAG store, final downstream resources, and printer queues.
* **Gray (External Systems & Clients)**: Input databases, Angular UI frontend, and external LLM APIs.

---

## Hybrid Architecture & Intent-Based Data Flow

This diagram illustrates how user queries are classified by the **IntentRouter**, dispatched across Spring Boot REST endpoints and Pinecone Cloud Vector RAG, aggregated into a unified context, and processed through Google Gemini / OpenRouter with sub-second latency:

```mermaid
graph TD
    classDef client fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#ffffff;
    classDef router fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#ffffff;
    classDef spring fill:#7c2d12,stroke:#f97316,stroke-width:2px,color:#ffffff;
    classDef vector fill:#4c1d95,stroke:#a855f7,stroke-width:2px,color:#ffffff;
    classDef llm fill:#831843,stroke:#ec4899,stroke-width:2px,color:#ffffff;

    User[Angular UI / Client BOH Query]:::client --> FastAPI[FastAPI Controller /chat]:::client
    FastAPI --> Singleton[Singleton ChatbotService & IntentRouter]:::router
    
    Singleton --> IntentEngine[IntentRouter Classification]:::router
    
    IntentEngine -->|Route: SPRING_*| SpringBoot[Spring Boot REST Microservices]:::spring
    IntentEngine -->|Route: PINECONE| PineconeDB[Pinecone Cloud Vector Index]:::vector
    IntentEngine -->|Route: HYBRID| HybridGather[Async Context Aggregator]:::router
    IntentEngine -->|Route: GEMINI_ONLY| LLMManager[ProviderManager Engine]:::llm

    HybridGather --> SpringBoot & PineconeDB
    SpringBoot --> ContextBuilder[Unified Context Builder]:::router
    PineconeDB --> ContextBuilder
    
    ContextBuilder --> PromptEngine[PromptBuilder + Current System Date]:::router
    PromptEngine --> LLMManager
    
    LLMManager -->|Primary| Gemini[Google Gemini API]:::llm
    LLMManager -->|Fallback| OpenRouter[OpenRouter Llama 3.1 Gateway]:::llm
    
    Gemini & OpenRouter --> PostProcess[clean_chat_formatting Post-Processor]:::router
    PostProcess --> Response[0.82s Latency Output]:::client
```

### Hybrid Architecture Highlights

1. **Phase 2 Intent Router**: Classifies incoming queries into 9 Intent categories (`INVENTORY`, `RECIPE`, `SUPPLIER`, `PRICING`, `EXPIRATION`, `DASHBOARD`, `KNOWLEDGE`, `GENERAL_CHAT`, `SETTINGS`) and routes to 4 execution paths:
   * **`SPRING_*`**: Direct REST query to Spring Boot backend (`/api/inventory`, `/api/recipes`, `/api/suppliers`, `/api/expiration/expiring`, `/api/dashboard/summary`, `/api/settings`).
   * **`PINECONE`**: Cloud vector RAG search over 3,833+ static BOH culinary safety & pairing chunks (`pantrypulse-rag`).
   * **`HYBRID`**: Concurrent multi-source gathering combining live Spring Boot tables + Pinecone RAG + LLM reasoning.
   * **`GEMINI_ONLY`**: Direct low-latency conversational chat for casual BOH staff greetings.

2. **High-Speed Performance & Zero-Downtime Startup**:
   * **Singleton Handles**: `ChatbotService` and `IntentRouter` are initialized as in-memory Singletons, eliminating per-request creation overhead.
   * **Lazy Anchor Embeddings**: Anchor query embeddings are computed lazily on-demand, ensuring container startup completes in **0.1 seconds** and eliminating HTTP 502 connection refusal errors on Railway deployments.
   * **0.82-Second End-to-End Latency**: Sub-second execution supported by four-stage telemetry logging (`[TIMING 1]` to `[TIMING 4]`).

3. **Clean Presentation & Confidentiality**:
   * Automatically strips internal technical terms ("knowledge base", "Pinecone", "RAG context", "database").
   * Employs post-processing `clean_chat_formatting()` regex filters to transform messy Markdown asterisks (`* **Item:**`) into clean, elegant bullet points (`• Item:`).

4. **Corporate AI Procurement Assistant**:
   * Generates formal purchase requests for low-stock ingredients using the Combined Corporate Email Format (Polite Greetings, Structured Bullet-Point Details Table, Procurement Team Signature, and AI Assistant Footer).

---

## Resilient Multi-Provider Fallback Flowchart

PantryPulse employs a resilient, multi-tiered failover structure. The system queries LLM providers in a prioritized sequence, automatically recovering from rate limits, quota exhaustion, or API outages.

```mermaid
graph TD
    classDef ai fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#ffffff;
    classDef workflow fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#ffffff;
    classDef output fill:#4c1d95,stroke:#a855f7,stroke-width:2px,color:#ffffff;
    classDef default fill:#111827,stroke:#9ca3af,stroke-width:2px,color:#ffffff;

    User[User BOH Query]:::default --> Router[LLM Provider Manager]:::default
    
    Router -->|1. Primary| P1[Google Gemini API]:::ai
    P1 -->|Success| R1[Format response]:::workflow
    P1 -->|Fail / Quota / Timeout| P2[OpenRouter Gateway]:::ai
    
    P2 -->|Success| R1
    P2 -->|Fail| P3[Together AI API]:::ai
    
    P3 -->|Success| R1
    P3 -->|Fail| P4[Fireworks AI API]:::ai
    
    P4 -->|Success| R1
    P4 -->|Fail| P5[DeepSeek API Direct]:::ai
    
    P5 -->|Success| R1
    P5 -->|Fail| P6[Mistral API Direct]:::ai
    
    P6 -->|Success| R1
    P6 -->|Fail| P7[RAG-only Local Fallback]:::output
    
    P7 -->|Context Extractor| R2[Summarize Pinecone / FAISS context]:::workflow
    R1 & R2 --> Output[Actionable BOH Response]:::default
```

---

## Technology Stack

* **AI Microservice**: Python 3.11.9, FastAPI, Uvicorn, Pydantic v2
* **Enterprise Microservices**: Java 17, Spring Boot REST Framework (`pantrypulse-production.up.railway.app`)
* **Frontend Web Application**: Angular 16+, Dark Glassmorphism UI
* **Cloud Vector Store & Embeddings**: Pinecone Cloud Index (`pantrypulse-rag`, 384 dimensions), SentenceTransformers (`BAAI/bge-small-en-v1.5`), Local FAISS fallback
* **LLM Provider Gateway**: Google Gemini (`gemini-1.5-flash`), OpenRouter API Gateway (`meta-llama/llama-3.1-8b-instruct`), DeepSeek, Mistral
* **RAG Knowledge Base**: 9,132+ unique recipes, 45 BOH safety & first-aid protocols, 12 traditional Telugu lunar months calendar, dish pairings, and commercial supplier directory
* **Multilingual Engine**: Regex word-boundary tokenized detection (`re.findall(r'\b[a-z]+\b')`) supporting English, Telugu, and Tenglish (Roman Telugu)
* **Orchestration Framework**: OpenClaw (Sequential BOH workflow manager & application dispatcher)

---

## Quick Run Commands

Execute these commands in the terminal to configure, populate, start, and verify the services:

### 1. Populate Vector Stores
```powershell
# Build local FAISS semantic index
python scripts/enrich_knowledge.py
python scripts/build_embeddings.py

# Sync static Knowledge Base to Pinecone Cloud Vector Index
python scripts/sync_pinecone.py
```

### 2. Launch the FastAPI Uvicorn Server
```powershell
# Start the AI microservice server locally on port 8000
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Run Verification Test Suites
```powershell
# Run AI backend service unit tests
python -m unittest discover -s tests

# Run OpenClaw Orchestration & integration tests
python -m unittest discover -s openclaw/tests
```

---

For a detailed breakdown of directory contents and logic implementation, see [project_structure.md](file:///e:/TCWING_PRJ/ai-service/project_structure.md) and [Project_logic_explanation.md](file:///e:/TCWING_PRJ/ai-service/Project_logic_explanation.md).
