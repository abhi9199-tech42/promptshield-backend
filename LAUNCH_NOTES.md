# PromptShield Launch Notes

## Status: **READY FOR MVP LAUNCH**

The PromptShield platform has been successfully implemented with all core requirements for the MVP.

### Key Features Implemented
1.  **Core Engine**: Pre-Tokenization Intelligence Layer (PTIL) integration for semantic compression.
2.  **LLM Integration**: Real connectivity to OpenAI and Anthropic APIs.
3.  **Security**: 
    -   API Key Authentication (`X-API-Key`).
    -   PII Scrubbing (Redacts Emails, Phone #s, SSN, Credit Cards).
4.  **Semantic Drift Detection**: Tracks prompt versioning and flags inconsistencies in semantic interpretation.
5.  **Analytics**: Tracks token savings and latency.
6.  **Frontend**: Next.js Playground with Visualization and Analytics.

### Initial Credentials
An offline script was used to generate the initial Admin API Key.
-   **User**: `admin@promptshield.ai`
-   **API Key**: `sk-ps-7E-BH9GDWiV-JjG5lteIXg`
    *(Note: This key is stored in the local SQLite database. Use the scripts/create_user.py to generate more if needed.)*

### How to Run

#### Backend
1.  Navigate to `PromptShield` root.
2.  Ensure environment variables are set:
    -   `OPENAI_API_KEY=sk-...`
    -   `ANTHROPIC_API_KEY=sk-...`
3.  Run Server:
    ```bash
    uvicorn backend.app:app --reload
    ```

#### Frontend
1.  Navigate to `PromptShield/frontend`.
2.  Run Dev Server:
    ```bash
    npm run dev
    ```
3.  Open `http://localhost:9000`.
4.  Enter the API Key (`sk-ps-7E-BH9GDWiV-JjG5lteIXg`) in the playground settings to start executing prompts.

### Database
-  SQLite file located at `PromptShield/promptshield.db`.
-  Migrations managed via Alembic.
