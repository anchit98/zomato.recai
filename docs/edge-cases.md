# Edge Cases: AI-Powered Restaurant Recommendation System

This document lists detailed edge cases for the project defined in:

- `docs/problemstatement.md`
- `docs/phase-wise-architecture.md`

The edge cases are grouped phase-wise to align with implementation and testing.

## Severity and Handling Legend

- **High**: Can break recommendation quality, cause failures, or mislead users.
- **Medium**: Degrades quality/usability but system can still function.
- **Low**: Minor impact; mostly UX or consistency issue.

For each edge case, define:

- **Expected behavior**: What the system should do.
- **Handling strategy**: Suggested implementation approach.

---

## Phase 1: Data Ingestion and Preprocessing Edge Cases

### EC-01: Dataset source temporarily unavailable

- **Severity**: High
- **Scenario**: Hugging Face dataset endpoint times out or returns non-200 response.
- **Expected behavior**: Ingestion should fail gracefully and use last known good snapshot if available.
- **Handling strategy**:
  - Add retry with exponential backoff.
  - Keep local versioned snapshots.
  - Raise clear error with timestamp and source URL.

### EC-02: Schema drift in source dataset

- **Severity**: High
- **Scenario**: Column names/types change (for example, `rating` becomes `aggregate_rating`).
- **Expected behavior**: Pipeline detects mismatch before corrupting cleaned data.
- **Handling strategy**:
  - Validate incoming schema against expected schema contract.
  - Maintain a schema mapping layer with version support.
  - Fail fast with actionable logs.

### EC-03: Missing critical fields in many rows

- **Severity**: High
- **Scenario**: Large fraction of rows missing `location`, `cuisine`, `cost`, or `rating`.
- **Expected behavior**: Rows with unusable core fields are excluded or defaulted by policy.
- **Handling strategy**:
  - Define mandatory vs optional fields.
  - Add threshold-based quality gate (for example, stop if >X% critical missing).
  - Produce data quality report for transparency.

### EC-04: Duplicate restaurants with conflicting values

- **Severity**: Medium
- **Scenario**: Same restaurant appears multiple times with different ratings/cost.
- **Expected behavior**: Keep one canonical record per deduplication key.
- **Handling strategy**:
  - Use composite dedup key (name + location + address when available).
  - Resolve conflicts with deterministic rules (latest update/highest confidence source).

### EC-05: Inconsistent cost formats

- **Severity**: Medium
- **Scenario**: Cost values as strings, ranges, symbols, or mixed currencies.
- **Expected behavior**: Normalize to a single numeric or bounded representation.
- **Handling strategy**:
  - Parse cost strings robustly.
  - Convert to standard currency if possible; otherwise assign an "unknown" cost bucket.
  - Keep raw value for audit/debug.

### EC-06: Rating scale mismatch

- **Severity**: Medium
- **Scenario**: Ratings appear in mixed scales (0-5, 0-10, percentages).
- **Expected behavior**: Normalize all ratings to one agreed scale.
- **Handling strategy**:
  - Detect source scale by pattern/range.
  - Convert to a canonical scale (recommended: 0-5).
  - Validate outliers (for example, rating > max scale).

### EC-07: Multi-language or noisy text in cuisine/location

- **Severity**: Low
- **Scenario**: Typographic variants, abbreviations, misspellings, or multiple languages.
- **Expected behavior**: Normalized text should remain queryable.
- **Handling strategy**:
  - Apply lowercasing, trimming, accent handling, and synonym mapping.
  - Use alias dictionary for common city and cuisine spellings.

---

## Phase 2: User Preference and Input Edge Cases

### EC-08: Empty input request

- **Severity**: High
- **Scenario**: User sends no preferences.
- **Expected behavior**: Return a guided validation response with required minimum fields.
- **Handling strategy**:
  - Define minimum required fields (for example, location).
  - Return human-readable validation message.

### EC-09: Unsupported location

- **Severity**: Medium
- **Scenario**: User provides a location not present in dataset.
- **Expected behavior**: Avoid hard failure; suggest nearest/available alternatives.
- **Handling strategy**:
  - Check exact and fuzzy matches.
  - Suggest top available locations with similar names.

### EC-10: Invalid budget values

- **Severity**: Medium
- **Scenario**: Budget provided as text like "very cheap-ish" or negative number.
- **Expected behavior**: Map if possible; otherwise request correction.
- **Handling strategy**:
  - Maintain budget normalization rules and accepted enums.
  - Provide clear "accepted values" in error response.

### EC-11: Non-numeric or out-of-range minimum rating

- **Severity**: Medium
- **Scenario**: Rating entered as "excellent", 9/5, or -1.
- **Expected behavior**: Normalize if obvious, reject if invalid.
- **Handling strategy**:
  - Parse flexible formats.
  - Enforce canonical range validation.

### EC-12: Conflicting preferences

- **Severity**: High
- **Scenario**: User asks for "highly rated, very low budget, premium fine dining, in rare location."
- **Expected behavior**: Return best-effort recommendations and mention trade-offs.
- **Handling strategy**:
  - Treat some constraints as hard and others as soft.
  - Include constraint-relaxation logic and explain what was relaxed.

### EC-13: Unsafe or prompt-injection-like text in additional preferences

- **Severity**: High
- **Scenario**: User enters text trying to override system prompt or request hidden data.
- **Expected behavior**: Input is sanitized and treated only as preference text.
- **Handling strategy**:
  - Escape/sanitize user text before prompt insertion.
  - Use strict system instructions and output schema validation.

---

## Phase 3: Candidate Retrieval and Filtering Edge Cases

### EC-14: Zero candidates after hard filtering

- **Severity**: High
- **Scenario**: Strict filters produce no results.
- **Expected behavior**: Return graceful fallback with controlled filter relaxation.
- **Handling strategy**:
  - Relax constraints stepwise (for example, rating then budget).
  - Inform user which criteria were relaxed.

### EC-15: Too many candidates for LLM context window

- **Severity**: High
- **Scenario**: Filtered list is very large and exceeds prompt token budget.
- **Expected behavior**: Pre-rank and pass only top-N candidates.
- **Handling strategy**:
  - Apply deterministic scoring before LLM stage.
  - Enforce token-aware truncation with stable ordering.

### EC-16: Dominant popular-chain bias in candidate set

- **Severity**: Medium
- **Scenario**: Heuristic ranking repeatedly favors the same chains.
- **Expected behavior**: Ensure diversity without reducing relevance too much.
- **Handling strategy**:
  - Add diversity constraints (cuisine/area/price spread).
  - Penalize near-duplicate recommendations.

### EC-17: Ambiguous cuisine tags

- **Severity**: Medium
- **Scenario**: A restaurant has multiple cuisines; user asks for one niche cuisine.
- **Expected behavior**: Partial match should be supported with confidence scoring.
- **Handling strategy**:
  - Use weighted cuisine matching.
  - Prefer primary cuisine match where available.

### EC-18: Stale cached candidate data

- **Severity**: Medium
- **Scenario**: Cache includes outdated ratings/costs.
- **Expected behavior**: Use cache with freshness guarantees or refresh policy.
- **Handling strategy**:
  - Add TTL and cache versioning.
  - Expose "last updated" metadata in logs/internal responses.

---

## Phase 4: LLM Ranking and Explanation Edge Cases

### EC-19: LLM hallucinates restaurants not in candidate set

- **Severity**: High
- **Scenario**: Model invents names or adds unknown details.
- **Expected behavior**: Output must be grounded strictly in provided candidates.
- **Handling strategy**:
  - Enforce structured output (JSON schema).
  - Post-validate that all recommended IDs exist in candidate list.
  - Drop/repair invalid items and retry if needed.

### EC-20: LLM ignores user constraints

- **Severity**: High
- **Scenario**: Returned options violate budget/rating constraints without explanation.
- **Expected behavior**: Recommendations should comply or explicitly justify exceptions.
- **Handling strategy**:
  - Encode hard constraints in prompt.
  - Add post-ranking rule validator before final response.

### EC-21: Verbose, generic, or repetitive explanations

- **Severity**: Medium
- **Scenario**: Explanations are too long or nearly identical for all restaurants.
- **Expected behavior**: Keep concise, distinct, and evidence-based reasons.
- **Handling strategy**:
  - Set strict explanation length and style constraints.
  - Add repetition checks and regenerate when quality is low.

### EC-22: Malformed model output

- **Severity**: High
- **Scenario**: Output is invalid JSON or missing required fields.
- **Expected behavior**: Auto-recover where possible; otherwise return safe fallback.
- **Handling strategy**:
  - Use parser with repair attempt.
  - Retry with "format correction" prompt.
  - Fallback to deterministic ranking if retries fail.

### EC-23: LLM API timeout/rate limit

- **Severity**: High
- **Scenario**: API returns timeout, 429, or transient provider errors.
- **Expected behavior**: Service remains responsive with retries or fallback mode.
- **Handling strategy**:
  - Exponential backoff with jitter.
  - Circuit-breaker and graceful degraded response.
  - Optional fallback to non-LLM recommendation output.

### EC-24: Prompt token overflow

- **Severity**: High
- **Scenario**: Combined prompt + candidates exceed model token limit.
- **Expected behavior**: Request should be auto-trimmed, not fail unexpectedly.
- **Handling strategy**:
  - Precompute token budget.
  - Compress candidate descriptions and reduce N adaptively.

---

---

## Phase 5: API Layer and Backend Edge Cases

### EC-25: Malformed JSON request payload

- **Severity**: High
- **Scenario**: Frontend sends invalid JSON or missing mandatory keys (e.g., `location`).
- **Expected behavior**: Return 400 Bad Request with specific schema validation errors.
- **Handling strategy**:
  - Use Pydantic/FastAPI for automatic schema validation.
  - Return clear, machine-readable error codes.

### EC-26: Backend timeout on upstream LLM API

- **Severity**: High
- **Scenario**: The core recommendation pipeline takes longer than the API gateway timeout (e.g., 30s).
- **Expected behavior**: Return 504 Gateway Timeout or a cached/best-effort partial response.
- **Handling strategy**:
  - Implement async processing.
  - Add circuit breakers for the LLM connector.
  - Consider returning a "job ID" for long-running rankings.

### EC-27: Traffic spikes causing latency degradation

- **Severity**: Medium
- **Scenario**: Sudden increase in concurrent recommendation requests.
- **Expected behavior**: System degrades gracefully (e.g., rate-limiting) instead of crashing.
- **Handling strategy**:
  - Implement rate limiting per API key or IP.
  - Use a task queue for LLM requests if necessary.

### EC-28: Inconsistent schema between Backend and Frontend

- **Severity**: Medium
- **Scenario**: FE expects `rating` but BE returns `aggregate_rating` after an update.
- **Expected behavior**: System remains functional via versioned API endpoints.
- **Handling strategy**:
  - Implement API versioning (e.g., `/v1/`, `/v2/`).
  - Use shared TypeScript types or contract tests (OpenAPI).

---

## Phase 6: Frontend Web Application Edge Cases

### EC-29: UI layout breakage with long AI explanations

- **Severity**: Low
- **Scenario**: LLM produces a very long paragraph that breaks the card layout.
- **Expected behavior**: Explanation is truncated with a "read more" expansion.
- **Handling strategy**:
  - CSS `line-clamp` or dynamic truncation.
  - Enforce character limits at the backend level.

### EC-30: Network instability / API unavailability

- **Severity**: Medium
- **Scenario**: User loses internet mid-request or Backend is down.
- **Expected behavior**: Show a user-friendly "Offline" or "Retry" state without crashing.
- **Handling strategy**:
  - Global error boundary and toast notifications.
  - Implement optimistic UI or retry logic.

### EC-31: Slow loading without feedback

- **Severity**: Low
- **Scenario**: LLM takes 5 seconds to respond; screen remains blank.
- **Expected behavior**: Show skeleton screens or shimmer animations to indicate progress.
- **Handling strategy**:
  - Progressive loading states for different phases of the result.

### EC-32: Search results empty state UX

- **Severity**: Low
- **Scenario**: No restaurants found for specific filters.
- **Expected behavior**: Show helpful "No results" message with suggestions to relax filters.
- **Handling strategy**:
  - Provide "Quick Relax" buttons (e.g., "Show all budgets").

---

## Phase 7: Quality, Monitoring, and Operations Edge Cases

### EC-33: Silent quality regression after prompt changes

- **Severity**: High
- **Scenario**: Prompt update reduces relevance without causing errors.
- **Expected behavior**: Detected via automated regression benchmarking.
- **Handling strategy**:
  - Run LLM-as-a-judge evaluations on a golden dataset.

### EC-34: PII leakage in logs

- **Severity**: High
- **Scenario**: User location or queries are logged in plain text.
- **Expected behavior**: PII is masked or redacted before reaching logs.
- **Handling strategy**:
  - Implement log scrubbing for sensitive fields.

### EC-35: Observability gaps

- **Severity**: Medium
- **Scenario**: Failure occurs in production but can't be traced back to the specific LLM call.
- **Expected behavior**: Every request has a unique Request-ID tied to all phase logs.
- **Handling strategy**:
  - Structured logging with correlation IDs.

---

## Cross-Cutting Edge Cases (Applies Across Phases)

### EC-36: Partial subsystem outage

- **Severity**: High
- **Scenario**: LLM is down but Retrieval is healthy.
- **Expected behavior**: Return deterministic recommendations with a note: "AI analysis currently unavailable."
- **Handling strategy**:
  - Fallback to heuristic ranking service.


### EC-37: Timezone and "open now" interpretation mismatch

- **Severity**: Medium
- **Scenario**: If operational hours are introduced, recommendation may be wrong by timezone.
- **Expected behavior**: Time-sensitive logic should use user-local timezone.
- **Handling strategy**:
  - Normalize timestamps and timezone handling centrally.

### EC-38: Localization mismatch

- **Severity**: Low
- **Scenario**: User language and system output language differ.
- **Expected behavior**: Response should respect user language preference where possible.
- **Handling strategy**:
  - Add output language parameter.
  - Keep internal canonical data language-independent.

---

## Phase 9: Mobile Compatibility Edge Cases

### EC-39: Narrow viewport layout shift

- **Severity**: Medium
- **Scenario**: Screen width < 375px (e.g., iPhone SE) causes overlapping text, hidden buttons, or broken card layouts.
- **Expected behavior**: Layout remains 100% readable and interactive via responsive scaling and stacking.
- **Handling strategy**:
  - Use Tailwind `flex-col` for mobile-first stacking.
  - Enforce minimum tap targets (44px x 44px) for all interactive elements.
  - Test UI on various small devices using browser simulation.

### EC-40: Touch latency and "ghost" interactions

- **Severity**: Low
- **Scenario**: Rapid tapping on filters or "Trending" buttons causes double-triggering or race conditions.
- **Expected behavior**: Inputs are debounced, and users receive immediate visual feedback (shimmer/spinners) on touch.
- **Handling strategy**:
  - Implement `useDebounce` on search triggers.
  - Add `active:scale-95` transitions to provide tactile feedback.

### EC-41: Disrupted connectivity (3G/Edge/High Latency)

- **Severity**: Medium
- **Scenario**: Large JSON payloads from the LLM time out or fail to load on unstable mobile networks.
- **Expected behavior**: The UI should indicate "Network is slow" and provide a retry option rather than a generic crash.
- **Handling strategy**:
  - Implement progressive loading (Skeleton screens).
  - Optimize the JSON payload size by removing unnecessary metadata.
  - Set adaptive timeouts for mobile clients.

---

## Phase 10: Multi-Cloud Deployment Edge Cases

### EC-42: CORS policy blocking production requests

- **Severity**: High
- **Scenario**: The production Vercel frontend cannot communicate with the Render backend because the origin is not explicitly allowed.
- **Expected behavior**: API requests from the allowed frontend domain succeed with 200 OK.
- **Handling strategy**:
  - Configure `CORSMiddleware` in FastAPI to include the specific Vercel production and preview URLs.
  - Verify pre-flight OPTIONS requests in the production environment.

### EC-43: Environment variable mismatch (Local vs Production)

- **Severity**: High
- **Scenario**: Critical keys like `GROQ_API_KEY` or `SUPABASE_ANON_KEY` are missing from the Render or Vercel dashboard.
- **Expected behavior**: System fails fast with a clear "Missing Environment Variable" error in logs.
- **Handling strategy**:
  - Implement a `check_env()` function during backend startup.
  - Use Vercel/Render "Secret Management" features and cross-verify keys.

### EC-44: Render "Cold Start" latency

- **Severity**: Medium
- **Scenario**: On the free tier, Render spins down the service after 15 mins of inactivity, causing the first request to take 30s+.
- **Expected behavior**: Frontend handles the long wait gracefully with a "Waking up the AI Scout..." status.
- **Handling strategy**:
  - Implement a "Keep-Alive" cron job (e.g., using GitHub Actions or a free uptime monitor) to ping the `/api/v1/health` endpoint.
  - Update frontend loading states to distinguish between "Thinking" and "Connecting to Server".

## Phase 11: Concurrency Handling & Performance Optimization Edge Cases

### EC-45: Temp file collision under concurrent requests

- **Severity**: High
- **Scenario**: Two users submit recommendations simultaneously with the same `session_id`. Both requests write to `pref_{session_id}.json` and `cand_{session_id}.json`, causing one request to read the other's data.
- **Expected behavior**: Each request operates on fully isolated temporary files, regardless of session overlap.
- **Handling strategy**:
  - Replace `session_id`-based filenames with `uuid4()`-based filenames (e.g., `pref_a1b2c3d4.json`).
  - Use Python's `tempfile.NamedTemporaryFile` or `tempfile.TemporaryDirectory` for automatic cleanup.
  - Delete temp files in a `finally` block to prevent orphans.

### EC-46: LLM rate-limit cascade (429 storm)

- **Severity**: High
- **Scenario**: 10+ users submit recommendations simultaneously. All 10 fire parallel Groq API calls. Groq returns 429 (Too Many Requests) for most of them, triggering exponential backoff retries that amplify the load.
- **Expected behavior**: The system caps concurrent LLM calls and queues excess requests, preventing a retry storm.
- **Handling strategy**:
  - Introduce an `asyncio.Semaphore(3)` (or `threading.Semaphore`) to cap concurrent Groq calls.
  - Queue excess requests with a configurable timeout (e.g., 15s).
  - If the queue is full or timeout is exceeded, immediately return deterministic fallback results.
  - Log throttled requests for operational visibility.

### EC-47: DataFrame reload storm on `/locations`

- **Severity**: Medium
- **Scenario**: 50 users hit the `/locations` endpoint simultaneously. Each call triggers `pd.read_csv()`, loading a ~5MB CSV into memory 50 times in parallel.
- **Expected behavior**: The CSV is loaded once and served from an in-memory cache.
- **Handling strategy**:
  - Load the DataFrame once during `RecommendationService.__init__()` and cache it as an instance variable.
  - Expose a `/admin/cache-refresh` endpoint for manual cache invalidation.
  - Add a TTL-based auto-refresh (e.g., every 24 hours) for long-running deployments.

### EC-48: Race condition in shared service state

- **Severity**: Medium
- **Scenario**: The single `RecommendationService` instance is shared across all FastAPI worker threads. If any method modifies instance-level state (e.g., a counter or cache dict) without locking, concurrent reads/writes produce incorrect results.
- **Expected behavior**: All shared mutable state is protected by thread-safe primitives.
- **Handling strategy**:
  - Use `threading.Lock()` for any mutable instance attributes.
  - Prefer immutable/request-scoped data over shared mutable state.
  - Audit all service methods for side effects on `self.*`.

### EC-49: Memory exhaustion under sustained load

- **Severity**: High
- **Scenario**: Each recommendation request loads the full DataFrame, creates JSON artifacts, and holds LLM response data in memory. Under 20+ concurrent requests, the Render instance (512MB RAM on free tier) runs out of memory and is OOM-killed.
- **Expected behavior**: Memory usage is bounded and predictable regardless of concurrency level.
- **Handling strategy**:
  - Cache the DataFrame once (single copy in memory).
  - Stream or discard intermediate JSON artifacts instead of accumulating them.
  - Set `WEB_CONCURRENCY=1` and rely on the LLM semaphore to bound parallel work.
  - Monitor memory via Render metrics and alert on threshold breaches.

### EC-50: Session isolation failure in history writes

- **Severity**: High
- **Scenario**: User A's recommendations are accidentally saved under User B's `session_id` due to a variable reference bug or async timing issue.
- **Expected behavior**: Each history write is strictly scoped to the originating request's session ID.
- **Handling strategy**:
  - Pass `session_id` as a function parameter (not stored on `self`).
  - Validate `session_id` format (UUID) before writing.
  - Add integration tests that simulate interleaved writes and verify isolation.

### EC-51: Background task failure (silent history loss)

- **Severity**: Medium
- **Scenario**: History persistence is moved to a `BackgroundTask`. The Supabase write fails (network error, auth expired), but since it's running in the background, the error is never surfaced to the user or logged.
- **Expected behavior**: Background task failures are logged with full context and optionally retried.
- **Handling strategy**:
  - Wrap background tasks in try/except with structured logging.
  - Implement a dead-letter queue or retry buffer for failed writes.
  - Expose a `/admin/failed-writes` endpoint for operational debugging.

### EC-52: Stale cache serving outdated data

- **Severity**: Low
- **Scenario**: The restaurant dataset is updated (new restaurants added, ratings changed), but the in-memory cache still holds the old version.
- **Expected behavior**: Cache is refreshable without server restart.
- **Handling strategy**:
  - Implement a cache TTL (e.g., 24 hours).
  - Add a protected `/admin/cache-refresh` endpoint.
  - Log cache age in telemetry so staleness is observable.

### EC-53: Thundering herd on cold start

- **Severity**: Medium
- **Scenario**: After a Render cold start, multiple users hit the service simultaneously. All requests trigger full initialization (DataFrame load, Supabase client creation, LLM warm-up) at the same time.
- **Expected behavior**: Initialization happens once; subsequent requests wait for it to complete rather than duplicating work.
- **Handling strategy**:
  - Use a `threading.Event` or `asyncio.Event` as an initialization gate.
  - First request triggers init; all others block until the gate is set.
  - Return a 503 "Service Warming Up" response if init takes too long.

---

## Fallback Plan: Multi-Level Resilience

In the event of failure at any layer of the ZOMATO REC.AI pipeline, the following fallback strategies are applied automatically:

### Level 1: LLM Fallback (Partial Pipeline Failure)
- **Trigger**: Groq API timeout, Rate Limit (429), or Malformed JSON output.
- **Strategy**: 
  - **Deterministic Ranking**: If the AI scout is unavailable, the system reverts to a heuristic ranking algorithm.
  - **Logic**: Sorts the Phase 3 candidate set by `rating` (descending) and `cost_match` (within budget).
  - **UX**: User is notified: *"Showing top results based on ratings while our AI Scout is busy."*

### Level 2: Data/Retrieval Fallback (Core Pipeline Failure)
- **Trigger**: Data ingestion failure or candidate retrieval service downtime.
- **Strategy**: 
  - **Popular Cache**: Return a static, pre-cached list of top-rated restaurants for the requested city/area.
  - **Logic**: Use a small, hardcoded "Hall of Fame" dataset as a safety net.

### Level 3: Connectivity Fallback (Infrastructure Failure)
- **Trigger**: Backend service unreachable or DNS failure.
- **Strategy**: 
  - **Offline Mode UI**: The frontend displays a "Currently Under Maintenance" or "Connection Lost" screen.
  - **Logic**: Implement a global error boundary in React to catch 503/504 errors and provide a manual "Reconnect" button.

### Level 4: Platform Outage Fallback (Regional Failure)
- **Trigger**: Full Vercel or Render regional outage.
- **Strategy**: 
  - **Static Maintenance Page**: DNS failover or a simple static page hosted on a secondary provider (e.g., GitHub Pages) to provide status updates and an ETA for restoration.

### Level 5: Concurrency Overload Fallback (Capacity Failure)
- **Trigger**: LLM semaphore queue is full, memory usage exceeds threshold, or request rate exceeds the per-IP limit.
- **Strategy**:
  - **Immediate Deterministic Response**: Bypass the LLM entirely and return heuristic-ranked results with a note: *"Our AI Scout is experiencing high demand. Here are top-rated matches based on your filters."*
  - **Rate Limit Response**: Return 429 with a `Retry-After` header and a user-friendly message: *"You're searching too fast! Please wait a few seconds."*
  - **Circuit Breaker**: If error rate exceeds 50% over a 60-second window, automatically switch all requests to deterministic mode for a cool-down period.

---

## Recommended Test Matrix

Use these categories to convert edge cases into tests:

- **Unit tests**: schema validation, input normalization, filter logic, output parser.
- **Integration tests**: dataset-to-candidate pipeline, candidate-to-LLM orchestration.
- **Contract tests**: response schema guarantees for UI/API.
- **Resilience tests**: timeout, retry, rate limit, and fallback behavior.
- **Quality tests**: ranking relevance checks on benchmark scenarios.
- **Mobile responsiveness**: testing viewports from 320px to 4k.
- **Deployment smoke tests**: CORS verification, SSL check, and cold-start measurement.
- **Concurrency tests**: Simulated parallel requests verifying file isolation, cache correctness, and LLM semaphore behavior.
- **Load tests**: Sustained traffic simulation (e.g., 20 concurrent users for 5 minutes) measuring p50/p95/p99 latency and error rates.

## Priority Implementation Order

Implement safeguards in this order for maximum risk reduction:

1. EC-01, EC-02, EC-14, EC-19, EC-22, EC-23, EC-31, EC-36
2. EC-42, EC-43 (Deployment stability)
3. EC-45, EC-46, EC-49, EC-50 (Concurrency — High severity)
4. EC-39, EC-41 (Mobile stability)
5. EC-03, EC-12, EC-15, EC-20, EC-29, EC-30
6. EC-47, EC-48, EC-51, EC-53 (Concurrency — Medium severity)
7. Remaining medium and low severity cases

