# KitchenSync & OpenClaw Project Logic Explanation

This document explains the full directory structure, module files, and the logic implemented inside each component of the KitchenSync AI microservice and the OpenClaw Orchestration engine.

---

## Application Core Module (`app/`)

The `app/` folder contains the FastAPI backend codebase that exposes individual AI microservices.

### API Controllers (`app/api/`)

* **`chat.py`**: Mounts `POST /chat`. Validates incoming queries and triggers the hybrid chatbot service.
* **`optimization.py`**: Mounts `POST /optimization`. Captures stock data and initiates the inventory optimizer service.
* **`recipe.py`**: Mounts `POST /recipe`. Captures ingredient parameters to generate compatible recipes.
* **`menu.py`**: Mounts `POST /menu`. Planner route accepting inventory details to suggest daily specials.
* **`pricing.py`**: Mounts `POST /pricing`. Accepts dish parameters and calculates profit margins.
* **`description.py`**: Mounts `POST /description`. Evaluates recipe names to construct elegant descriptions.
* **`supplier.py`**: Mounts `POST /supplier`. Mounts supplier replenishment messaging workflows.

### Prompts & Instructions (`app/prompts/`)

* **`system_prompt.py`**: Core persona boundaries, forcing professional, brief, and emoji-free text.
* **`chatbot_prompt.py`**: Directs the chatbot on hybrid search details, multilingual checks, and fallback formatting.
* **`inventory_prompt.py`**: Instructs the LLM to write clean restaurant names, flag purchase requests, and note ingredient shelf-lives.
* **`pricing_prompt.py`**: Establishes instructions for strategy, positioning, and price confidence values.
* **`supplier_prompt.py`**: Directs the drafting of purchase order messages with urgency levels and subjects.

### Core Business Services (`app/services/`)

* **`chatbot_service.py`**: Implements hybrid search, exact database index match fallbacks, multilingual script verification, and formatting cleansers.
* **`inventory_optimizer_service.py`**: Programmatically merges duplicates, overrides priorities to `HIGH` for short-expiry ingredients (1-2 days), and computes low-stock items for purchase recommendations.
* **`recipe_service.py`**: Standardizes recipe details, calculates confidence metrics, and sorts recommendations by match counts and preparation times.
* **`menu_service.py`**: Programmatically intersects matched inventory to prevent hallucinated ingredients, intersects missing items list, formats estimated profit to rupee strings, and ranks specials by urgency.
* **`pricing_service.py`**: Standardizes pricing suggestions, maps strategies based on margins, and returns confidence.
* **`description_service.py`**: Scrubs scraped site fragments and applies restaurant menu fallback layouts.
* **`supplier_service.py`**: Integrates multi-item replenishment, unescapes newline draft characters, and builds order tracking IDs.

### Request & Response Schemas (`app/schemas/`)

* **`request.py`**: Enforces strict request constraints (e.g. `min_length=1` for arrays, non-negative bounds).
* **`response.py`**: Formats standardized FastAPI JSON responses wrapper (`ApiResponse[T]`).

### Knowledge Base Database (`app/knowledge/`)

* Static JSON databases of recipes, pairings, chef notes, suppliers, seasonal items, and safety checklists.

### Retrieval & LLM Adapters (`app/rag/` & `app/llm/`)

*   **`retriever.py`**: Wraps SentenceTransformers model and local FAISS indices to run similarity retrieval.
*   **`llm_router.py`**: Manages and routes generation requests to the centralized `ProviderManager`.
*   **`base_provider.py`**: Declares abstract class for LLM API integration.
*   **`provider_manager.py`**: central manager executing the fallback priority chain and triggering local RAG-only text summaries if all endpoints are offline.
*   **`provider_registry.py`**: Stores configured priorities and maps active API clients (Gemini, Grok, OpenRouter, Together, Fireworks, DeepSeek, Mistral).
*   **`health_monitor.py`**: Evaluates statuses and records latencies dynamically.
*   **`retry_manager.py`**: Retries transient rate-limits and network timeouts using exponential backoffs.

### Vector DB Retrievers (`app/retrievers/`)

*   **`base_retriever.py`**: Declares abstract interface for semantic query retrieval.
*   **`faiss_retriever.py`**: Implements local FAISS search.
*   **`pinecone_retriever.py`**: Implements cloud-hosted Pinecone search.

### DB Administration Scripts (`scripts/`)

*   **`upload_embeddings.py`**: Batch uploads FAISS database chunks and embeddings to the Pinecone cloud index.

---

## OpenClaw Orchestrator Module (`openclaw/`)

The `openclaw/` folder houses the workflow orchestation engine that executes downstream pipelines.

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

> [!NOTE]
> For a detailed blueprint of the project architecture and what AI features are implemented, open the:
>  **[Project Structure (project_structure.md)](file:///e:/TCWING_PRJ/ai-service/project_structure.md)**
