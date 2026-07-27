# PantryPulse & OpenClaw Project Logic Explanation

This document explains the full directory structure, module files, and the logic implemented inside each component of the PantryPulse AI microservice, Hybrid Routing System, and OpenClaw Orchestration engine.

---

## Application Core Module (`app/`)

The `app/` folder contains the FastAPI backend codebase that exposes AI microservices and manages hybrid orchestration.

### API Controllers & Proxy Routes (`app/api/`)

* **`chat.py`**: Mounts `POST /chat`. Validates incoming queries and triggers `HybridChatService` singleton execution.
* **`spring_proxy.py`**: Exposes `/api/proxy/*` endpoints forwarding live data requests directly to Spring Boot backend (`/api/inventory`, `/api/recipes`, `/api/suppliers`, `/api/historical-orders`, `/api/expiration/expiring`, `/api/dashboard/summary`, `/api/settings`).
* **`supplier.py`**: Mounts `POST /supplier`. Triggers `SupplierService` to generate formal corporate purchase request emails.
* **`optimization.py`**: Mounts `POST /optimization`. Captures stock data and initiates the inventory optimizer service.
* **`recipe.py`**: Mounts `POST /recipe`. Captures ingredient parameters to generate compatible recipes.
* **`menu.py`**: Mounts `POST /menu`. Planner route accepting inventory details to suggest daily specials.
* **`pricing.py`**: Mounts `POST /pricing`. Accepts dish parameters and calculates profit margins.
* **`description.py`**: Mounts `POST /description`. Evaluates recipe names to construct elegant descriptions.

### Prompts & Instructions (`app/prompts/`)

* **`prompt_builder.py`**: Formats system prompts, injects `Current System Date` (e.g. `2026-07-26`) for accurate expiration calculations, enforces strict confidentiality (forbids technical terms like "knowledge base", "Pinecone", "RAG"), and directs clean bullet-point styling (`• Item:`).
* **`system_prompt.py`**: Persona boundaries for standard, brief, and emoji-restricted BOH text responses.
* **`chatbot_prompt.py`**: Directs the chatbot on hybrid search details, multilingual checks, and fallback formatting.
* **`supplier_prompt.py`**: Enforces the Combined Corporate Email Format for supplier purchase requests (Greetings, Details Table, Procurement Team Signature, AI Assistant Footer).
* **`inventory_prompt.py`**: Instructs the LLM to write clean restaurant names, flag purchase requests, and note ingredient shelf-lives.
* **`pricing_prompt.py`**: Establishes instructions for strategy, positioning, and price confidence values.

### Query Intent Routing (`app/routing/`)

* **`intent_router.py`**: Implements Phase 2 Intent Detection. Classifies queries into 9 Intent categories (`INVENTORY`, `RECIPE`, `SUPPLIER`, `PRICING`, `EXPIRATION`, `DASHBOARD`, `KNOWLEDGE`, `GENERAL_CHAT`, `SETTINGS`) and routes to 4 execution paths (`SPRING_*`, `PINECONE`, `HYBRID`, `GEMINI_ONLY`). Uses **lazy anchor query embeddings** (`_get_anchor_embeddings`) to guarantee **0.1-second container startup** and zero 502 connection refusal errors on Railway deployments.

### Core Business Services & Aggregators (`app/services/`)

* **`hybrid_chat_service.py`**: Hybrid Orchestration Engine. Executes query routing, triggers `ContextBuilder` for live REST + RAG data, logs 4-stage telemetry timing (`[TIMING 1]` to `[TIMING 4]`), and applies post-processing `clean_chat_formatting()` regex filters to strip raw Markdown asterisks (`* **Item:**` -> `• Item:`).
* **`context_builder.py`**: Aggregates live Spring Boot REST endpoints (`/api/inventory`, `/api/recipes`, `/api/suppliers`, `/api/expiration/expiring`, `/api/dashboard/summary`) and Pinecone Cloud Vector RAG concurrently via `asyncio.gather()`.
* **`supplier_service.py`**: Generates corporate supplier purchase order request emails. Implements fallback templates for English and Telugu adhering to the Combined Corporate Procurement Format.
* **`spring_api.py`**: Async HTTP client (`SpringApiClient`) managing communication with Spring Boot REST microservices (`pantrypulse-production.up.railway.app`).
* **`chatbot_service.py`**: Singleton Chatbot Engine handle (`get_chatbot_service()`).
* **`inventory_optimizer_service.py`**: Merges duplicate stock items, overrides priorities to `HIGH` for short-expiry ingredients (1-2 days), and computes replenishment lists.
* **`recipe_service.py`**: Standardizes recipe details, calculates compatibility scores, and searches across master recipe datasets.
* **`menu_service.py`**: Intersects matched inventory to prevent hallucinated ingredients, formats estimated profit, and ranks specials.
* **`pricing_service.py`**: Standardizes pricing suggestions and maps strategies based on margins.
* **`description_service.py`**: Scrubs scraped site fragments and applies clean restaurant menu fallback layouts.

### Request & Response Schemas (`app/schemas/`)

* **`request.py`**: Enforces strict request constraints (`min_length=1`, non-negative bounds).
* **`response.py`**: Formats standardized FastAPI JSON response wrappers (`ApiResponse[T]`).

### Knowledge Base Database (`app/knowledge/`)

* Static JSON databases containing 9,132+ entries:
  * **`recipes.json`**: Andhra Pradesh district specialties (Kakinada, Bhimavaram, Guntur, Rayalaseema, Nellore, Vizag), Telangana, Tamil Nadu, Kerala, Karnataka, Goa, Maharashtra, and Punjab recipes.
  * **`pairing.json`**: Regional and seasonal dish pairings strictly adhering to master `{"ingredient": "...", "pairs": [...]}` schema.
  * **`safety.json`**: 45 master BOH kitchen safety, injury first-aid (Pasupu / turmeric on chopping cuts), and emergency protocols.
  * **`seasonal.json`**: Sub-seasons and 12 traditional Telugu lunar months calendar with festival menu recommendations.
  * **`chef_notes.json`**: Back-of-house culinary prep guidelines and best practices.
  * **`suppliers.json`**: Commercial ingredient and LPG cooking gas vendor details.

### Retrieval & LLM Adapters (`app/rag/` & `app/llm/`)

* **`retriever.py`**: Wraps SentenceTransformers model (`BAAI/bge-small-en-v1.5`) and vector stores for similarity retrieval.
* **`openrouter_client.py`**: Gateway integration for OpenRouter API (`meta-llama/llama-3.1-8b-instruct`).
* **`provider_manager.py`**: Central manager executing the failover priority chain (Gemini primary -> OpenRouter gateway -> DeepSeek/Mistral -> RAG fallback).
* **`provider_registry.py`**: Stores configured priorities and maps active API clients.
* **`health_monitor.py`**: Evaluates provider statuses and records latencies dynamically.
* **`retry_manager.py`**: Retries transient rate-limits and network timeouts using exponential backoffs.

### Vector DB Retrievers (`app/retrievers/`)

* **`pinecone_retriever.py`**: Implements cloud-hosted Pinecone search over the 384-dimension `pantrypulse-rag` index.
* **`faiss_retriever.py`**: Implements local FAISS search fallback.
* **`base_retriever.py`**: Declares abstract interface for semantic query retrieval.

### DB Administration Scripts (`scripts/`)

* **`sync_pinecone.py`**: Syncs all 7 static Knowledge Base JSON files to the Pinecone Cloud Vector Index (`pantrypulse-rag`).
* **`build_embeddings.py`**: Builds local FAISS semantic database index chunks.
* **`enrich_knowledge.py`**: Populates master recipe datasets.

---

## OpenClaw Orchestrator Module (`openclaw/`)

The `openclaw/` folder houses the workflow orchestration engine that executes downstream pipelines.

### Workflow Blueprints (`openclaw/workflows/`)

* **`restaurant_workflow.py`**: Coordinates the sequential data-flow. Intercepts and pipes inputs from Optimization output to Recipe, Recipe recommendations to Menu, and Optimization low stock flags to Supplier orders.

### Downstream Operations & Print Queue (`openclaw/operations/`)

* **`print_queue.py`**: Simulated thread-safe queue. Enqueues menu specials print jobs with ISO 8601 timestamps.
* **`workflow_status.py`**: Tracks workflow lifecycle run states (`PENDING`, `RUNNING`, `PARTIAL_SUCCESS`, `COMPLETED`).
* **`execution_log.py`**: Records milestone execution timings and error warning arrays.
* **`completion_manager.py`**: Combines dispatcher publishing, status updates, and print queue enqueuing.

### Adapters & Dispatchers (`openclaw/integration/`)

* **`application_dispatcher.py`**: Fan-out publisher translating the compiled plan into Dashboard, Menu, Supplier, and Reports modules.
* **`reports_adapter.py`**: Aggregates statistics and formats `report_timestamp` as a clean ISO 8601 string.

---

For a detailed blueprint of the project architecture and implemented AI features, see [README.md](file:///e:/TCWING_PRJ/ai-service/README.md) and [project_structure.md](file:///e:/TCWING_PRJ/ai-service/project_structure.md).
