# Phase-Wise Architecture: AI-Powered Restaurant Recommendation System

This document defines a phased architecture for implementing the restaurant recommendation system described in `docs/problemstatement.md`.

## High-Level Architecture

The system is implemented as a pipeline with seven layers:

1. **Data Layer** - ingestion, cleaning, normalization, storage.
2. **Preference Layer** - captures and validates user preferences.
3. **Retrieval and Filtering Layer** - applies deterministic filtering and candidate generation.
4. **LLM Intelligence Layer** - ranking and explanation generation.
5. **Persistence Layer** - stores user sessions and recommendation history.
6. **API Layer** - exposes recommendation logic and history via REST endpoints.
7. **Frontend Layer** - modern web interface for interaction and history browsing.
8. **Observability Layer** - logging, monitoring, and quality evaluation.

---

## Phase 1: Foundation and Data Setup

### Goal

Prepare clean and queryable restaurant data from the source dataset.

### Components

- Dataset loader (Hugging Face source)
- Data cleaning and normalization module
- Schema mapper for key fields
- Local storage/cache (CSV/JSON/SQLite, based on implementation choice)

### Key Activities

- Download and inspect the dataset.
- Remove duplicates and handle missing values.
- Normalize location, cuisine, cost, and ratings.
- Define canonical data schema for downstream modules.

### Deliverables

- Cleaned dataset artifact
- Data schema definition
- Data quality report (missing values, invalid rows, duplicates removed)

### Exit Criteria

- Data can be reliably queried by location, budget, cuisine, and rating.
- Critical fields required by recommendation flow are complete or safely defaulted.

---

## Phase 2: User Preference and Input Layer

### Goal

Create a robust interface to collect user intent and constraints.

### Components

- Input form/API endpoint
- Request validation module
- Preference model object

### Key Activities

- Capture user preferences:
  - Location
  - Budget band (low/medium/high)
  - Cuisine
  - Minimum rating
  - Additional preferences
- Validate and sanitize inputs.
- Convert input into a standardized internal preference object.

### Deliverables

- Input contract (request schema)
- Validation rules and error messages
- Preference object used by filtering and prompt builder

### Exit Criteria

- Invalid requests fail gracefully with clear messages.
- Valid requests consistently produce normalized preference objects.

---

## Phase 3: Candidate Retrieval and Rule-Based Filtering

### Goal

Generate high-quality candidate restaurants before calling the LLM.

### Components

- Filter engine
- Candidate scorer (optional heuristic score)
- Top-N selector

### Key Activities

- Apply hard filters: location, minimum rating, and budget constraints.
- Apply soft matching: cuisine relevance and extra preferences.
- Limit results to a candidate set for LLM processing (for cost and latency control).

### Deliverables

- Candidate generation service
- Filtering logic documentation
- Fallback strategy when strict filters return zero results

### Exit Criteria

- Candidate set quality is acceptable for recommendation generation.
- Empty-result scenarios are handled predictably.

---

## Phase 4: LLM Ranking and Explanation Layer

### Goal

Use an LLM to produce ranked, human-readable recommendations.

### Components

- Prompt builder
- LLM connector/client
- Response parser and guardrails

### Key Activities

- Build structured prompts using user preferences + candidate data.
- Ask LLM to rank candidates and explain relevance.
- Parse and validate output format.
- Add guardrails to reduce hallucinations and enforce grounded responses.

### Deliverables

- Prompt template(s)
- LLM orchestration module
- Structured recommendation response model

### Exit Criteria

- Output is consistent, explainable, and tied to candidate data.
- Recommendations can be parsed and rendered without manual cleanup.

---

---

---

## Phase 5: Session Management and Persistent History

### Goal

Enable users to track, retrieve, and manage their past recommendation requests.

### Components

- **Supabase Project**: Cloud-hosted Postgres instance with built-in Auth and REST API.
- **Supabase Python Client**: `supabase` library for asynchronous database interactions.
- **Session Service**: Logic to associate requests with unique user sessions or IDs.

### Key Activities

- **Supabase Setup**: Create a new project and initialize `user_history` and `recommendations` tables.
- **Schema Implementation**: Define relational schema for storing preference objects (JSONB) and LLM outputs.
- **Integration**: Implement the `HistoryService` using Supabase client to UPSERT records.
- **Security**: Configure Row Level Security (RLS) if user authentication is implemented.

### Deliverables

- Database schema migration scripts.
- History management service layer.
- API endpoints for history retrieval (e.g., GET `/api/v1/history`).

### Exit Criteria

- Every user request is safely persisted with its resulting recommendations.
- History can be retrieved by session in < 1s.

---

## Phase 6: API Layer and Backend Application

### Goal

Wrap the recommendation pipeline and history service in a robust backend service.

### Components

- **API Framework**: FastAPI or Flask for high-performance REST endpoints.
- **Service Orchestrator**: Logic to coordinate Phase 2, 3, 4, and 5.
- **Schema Models**: Pydantic models for request/response validation.

### Key Activities

- Implement POST `/api/v1/recommend` and GET `/api/v1/history` endpoints.
- Integrate the persistence layer (Phase 5) into the main recommendation flow.
- Add authentication/session-key middleware to distinguish users.
- Implement API documentation (Swagger/OpenAPI).

### Deliverables

- Unified backend service source code.
- API documentation with history endpoint specs.
- Database integration tests.

### Exit Criteria

- Backend processes recommendations and history requests consistently.
- Session-based history is accessible via the API.

---

## Phase 7: Frontend Web Application

### Goal

Build a premium interface with integrated history management.

### Components

- **UI Framework**: Next.js, Vite + React, or similar.
- **History Sidebar/View**: A dedicated section for users to browse past results.
- **Components**: 
  - Search interface.
  - Recommendation cards.
  - History Dashboard (clickable past queries).

### Key Activities

- Implement a "History" tab or sidebar in the UI.
- Allow users to re-load past recommendations from their history.
- Ensure the UI state syncs with the Backend session history.

### Deliverables

- Frontend source code with history support.
- Interactive UI components for history browsing.

### Exit Criteria

- Users can see a list of their past searches and re-examine AI explanations.

---

## Phase 8: Quality, Monitoring, and Iteration

### Goal

Improve reliability, relevance, and operational readiness.

### Components

- Evaluation suite
- Logging and analytics module
- Feedback loop system

### Key Activities

- Track quality metrics (relevance, explainability, user satisfaction).
- Measure performance metrics (latency, token usage, failure rates).
- Add tests for ingestion, filtering, prompt generation, and response parsing.
- Use user feedback to improve prompts and ranking strategy.

### Deliverables

- Test suite (unit + integration)
- Monitoring dashboard metrics definition
- Iteration plan for continuous improvement

### Exit Criteria

- System meets agreed quality and performance thresholds.
- Team has observability and a repeatable improvement process.

---

## Phase 9: Mobile Compatibility & Responsive Refinement

### Goal

Ensure ZOMATO REC.AI provides a premium, "vibe-first" experience on mobile devices.

### Components

- **Mobile-Responsive Layout**: Tailwind-based adaptive grid and container system.
- **Touch Interaction Layer**: Swipe gestures and touch-optimized buttons.
- **Adaptive UI**: Bottom-sheet drawers for Trending searches on small screens.

### Key Activities

- Implement mobile-first responsive breakpoints (sm, md, lg).
- Optimize the SearchForm for high thumb-reachability on mobile.
- Refactor the Sidebar into a standard Drawer/Bottom-sheet for mobile viewports.
- Audit performance for mobile browsers (latency, asset size).

### Deliverables

- Fully responsive Frontend UI.
- Mobile-specific interaction components.
- Mobile browser compatibility report.

### Exit Criteria

- The application is fully functional and visually stunning on standard mobile viewports (iPhone/Android).
- Search and Trending interactions feel native and fluid on touch screens.

---

## Phase 10: Multi-Cloud Deployment (Vercel & Render)

### Goal

Deploy ZOMATO REC.AI to a public production environment with robust CI/CD.

### Components

- **Frontend Hosting (Vercel)**: Global CDN for the Next.js application.
- **Backend Hosting (Render)**: Managed Web Service for the FastAPI/Python engine.
- **Environment Management**: Unified secret management across platforms.

### Key Activities

- Configure Production CORS policy to allow the Vercel URL on the Render backend.
- Set up automated deployments via GitHub (push-to-deploy).
- Optimize the Render service for cold-starts and memory usage.
- Centralize production logs and telemetry for monitoring.

### Deliverables

- Live production URL (Vercel).
- Stable production API endpoint (Render).
- Integrated production monitoring dashboard.

### Exit Criteria

- Users can access the platform via a public URL.
- The platform successfully handles real-world traffic with production-grade uptime.

---

- **Milestone 1:** Phases 1-2 complete (Data prep & Input logic).
- **Milestone 2:** Phases 3-4 complete (Core LLM Recommendation Engine stable).
- **Milestone 3:** Phase 5 complete (Supabase project linked and schema deployed).
- **Milestone 4:** Phase 6 complete (Unified Backend API with history endpoints).
- **Milestone 5:** Phase 7 complete (Frontend Web App with History UI).
- **Milestone 6:** Phase 8 complete (Production-ready with monitoring & tests).
- **Milestone 7:** Phase 9 complete (Mobile-ready and touch-optimized).
- **Milestone 8:** Phase 10 complete (Publicly deployed to Vercel & Render).

## Dependencies Between Phases

- Phase 2 depends on Phase 1 schema.
- Phase 3 depends on Phase 2 output.
- Phase 4 depends on Phase 3 candidates.
- Phase 5 can be implemented in parallel with Phase 4 but is needed for Phase 6.
- Phase 6 integrates Phases 2, 3, 4, and 5.
- Phase 7 depends on Phase 6 API.
- Phase 8 monitors all layers.
- Phase 9 builds upon the stable Phase 7 UI.
- Phase 10 deploys the complete stack.
