# PromptShield - Development Tasks

## Phase 1: Project Initialization & Architecture
- [x] **1.1 Structure Setup**: Create `backend/`, `frontend/`, `scripts/` directories. <!-- id: 1.1 -->
- [x] **1.2 Environment Config**: Initialize Python venv, create `requirements.txt` (FastAPI, SQLAlchemy, etc.), and `package.json`. <!-- id: 1.2 -->
- [x] **1.3 PTIL Integration**: Verify `Pre-Tokenization Intelligence Layer (PTIL)` is importable by the new backend. Create a basic `engine.py` wrapper to test connectivity. <!-- id: 1.3 -->
- [x] **1.4 Git Setup**: Configure `.gitignore` for standard Python/Node/Env files. <!-- id: 1.4 -->

## Phase 2: Backend Core API Development
- [x] **2.1 API Scaffold**: Initialize FastAPI app (`app.py`), configure CORS, and basic error handling. <!-- id: 2.1 -->
- [x] **2.2 Database Models**: Design and implement SQLAlchemy models for `User`, `Prompt`, and `CompressedPrompt`. <!-- id: 2.2 -->
- [x] **2.3 Migrations**: Set up Alembic and run initial migration. <!-- id: 2.3 -->
- [x] **2.4 Endpoint - Standard**: Implement `POST /api/v1/compress` (Raw -> CSC). <!-- id: 2.4 -->
- [x] **2.5 Endpoint - Analysis**: Implement `POST /api/v1/analyze` (Detailed PTIL breakdown). <!-- id: 2.5 -->
- [x] **2.6 Service Health**: Add `GET /api/v1/health` endpoint. <!-- id: 2.6 -->

## Phase 3: LLM Integration layer
- [x] **3.1 Provider Base Class**: Create abstract `LLMProvider` interface. <!-- id: 3.1 -->
- [x] **3.2 Adapter - OpenAI**: Implement adapter for OpenAI (formatting, auth). <!-- id: 3.2 -->
- [x] **3.3 Adapter - Anthropic**: Implement adapter for Anthropic Claude. <!-- id: 3.3 -->
- [x] **3.4 Token Mapping**: Implement `TokenMapper` utility to compare Raw vs. CSC token counts using `tiktoken`. <!-- id: 3.4 -->
- [x] **3.5 Execute Endpoint**: Implement `POST /api/v1/execute` to chain Compression -> LLM -> Logging. <!-- id: 3.5 -->

## Phase 4: Data & Analytics Pipeline
- [x] **4.1 Activity Logging**: Implement logic to persist request metrics (latency, savings, models) to DB. <!-- id: 4.1 -->
- [x] **4.2 Analytics Service**: Create utility to aggregate savings (e.g., "Total Tokens Saved"). <!-- id: 4.2 -->
- [x] **4.3 Stats Endpoints**: Implement `GET /api/v1/stats/summary` and `/history`. <!-- id: 4.3 -->
- [x] **4.4 Replay Logic**: Implement `POST /api/v1/replay/{id}` to re-run semantic states. <!-- id: 4.4 -->

## Phase 5: Web Dashboard (Frontend)
- [x] **5.1 Next.js Init**: Initialize Next.js 14 project with Tailwind CSS. <!-- id: 5.1 -->
- [x] **5.2 Theme Setup**: Configure global styles (Dark mode, premium aesthetics). <!-- id: 5.2 -->
- [x] **5.3 Component - Playground**: Build Split-view component (Raw Input vs. CSC Output). <!-- id: 5.3 -->
- [x] **5.4 Component - Visualizer**: Create "Chip" visualization for ROOT, OPS, ROLES. <!-- id: 5.4 -->
- [x] **5.5 Component - Analytics**: Build charts for token savings history. <!-- id: 5.5 -->
- [x] **5.6 Integration**: Connect Frontend services to Backend API. <!-- id: 5.6 -->

## Phase 6: Polish & Deployment (Future)
- [x] **6.1 Dockerize**: Create Dockerfiles for Backend and Frontend. <!-- id: 6.1 -->
- [x] **6.2 Documentation**: Generate OpenAPI/Swagger docs. <!-- id: 6.2 -->
- [x] **6.3 Final QA**: Run e2e validation suite. <!-- id: 6.3 -->
