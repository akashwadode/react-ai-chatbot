# Project File Structure & Analysis

## Table of Contents
- [Redundant / Unused Files and Code](#1-redundant--unused-files-and-code)
- [Near-Duplicate Code](#2-near-duplicate-code)
- [File-by-File Explanation](#3-file-by-file-explanation)
  - [Backend Core](#backend-core)
  - [AI Module](#ai-module)
  - [Chat Module](#chat-module)
  - [Link Module](#link-module)
  - [Report Module](#report-module)
  - [WhatsApp Module](#whatsapp-module)
  - [Frontend](#frontend)

---

## 1. Redundant / Unused Files and Code

| Item | Why it's redundant |
|------|-------------------|
| `backend/__init__.py` | Empty file. FastAPI doesn't need it — the backend is run directly via `main.py`, not imported as a package. |
| `backend/FILE STRUCTURE.md` | Documentation only. Not used by any code. |
| `main.py` `/test`, `/test-db`, `/test-patient` endpoints | Debug/dev endpoints hardcoded with real DB queries. Should not exist in a real deployment. |
| Commented-out block in `whatsapp_router.py` (lines 64–95) | Dead code — the old single-notification version of `process-pending-new` was replaced but not deleted. |
| `POST /whatsapp/process-pending` + `send_whatsapp_template` + `fetch_pending_notification` | The older single-notification pipeline. Superseded by the `*_new` batch versions. Only kept as a manual test endpoint. |

---

## 2. Near-Duplicate Code

| Pair | What's duplicated |
|------|------------------|
| `send_whatsapp_template` vs `send_whatsapp_new_template` in `whatsapp_service.py` | Near-identical functions — same HTTP call, same structure. Only the template name and body parameters differ. |
| `fetch_pending_notification` vs `fetch_all_pending_notifications` in `whatsapp_repository.py` | Identical SQL query — only difference is `LIMIT 1`. One is a subset of the other. |
| `DEFAULT_BUTTONS` in `chat_service.py` (backend) and `Chat.jsx` (frontend) | The same list is hardcoded in both places independently. |

---

## 3. File-by-File Explanation

---

### Backend Core

#### `backend/main.py`
FastAPI app entry point. Registers all module routers, sets up CORS to allow requests from the frontend, and contains debug test endpoints (`/test`, `/test-db`, `/test-patient`).

#### `backend/__init__.py`
Empty file. Serves no purpose in this setup — the backend is run directly, not imported as a Python package.

#### `backend/FILE STRUCTURE.md`
Developer documentation describing the folder layout. Not used by any running code.

#### `backend/.env`
Environment variables file. Stores secrets such as database credentials, WhatsApp API token, and the signed URL secret. Should never be committed to version control.

#### `backend/requirements.txt`
Lists all Python dependencies needed to run the backend (e.g. FastAPI, psycopg2, requests, etc.).

#### `backend/core/database.py`
Contains a single function `get_connection()` that opens and returns a PostgreSQL database connection using psycopg2. Used by every module that needs to talk to the DB.

#### `backend/shared/cache.py`
Three in-memory caches used across the app:
- `_PARAMETERS_CACHE` — list of all lab parameter names, loaded once from the DB.
- `_PATIENT_CONTEXT_CACHE` — stores each patient's report as a text string and a parsed key-value dict.
- `_PATIENT_MEMORY_CACHE` — stores per-patient chat history for the LLM conversation context.

All caches reset when the server restarts.

---

### AI Module

#### `backend/modules/ai/llm.py`
Handles communication with a locally running Ollama instance (Mistral 7B model). Builds a messages array (system prompt + chat history + new user message) and sends it to the Ollama `/api/chat` endpoint. Returns the AI's text reply and appends the exchange to the chat history.

#### `backend/modules/ai/prompts.py`
Central store for all prompt templates. Contains:
- `SYSTEM_PROMPT` — instructs the LLM to act as a concise, patient-friendly medical report assistant.
- `build_user_prompt()` — formats the patient's question and their report data into an LLM-ready string.

---

### Chat Module

#### `backend/modules/chat/chat_router.py`
Defines the `POST /chat` endpoint. Validates the signed URL token (via `validate_signed_request` dependency) and passes the patient hash and question to the chat service.

#### `backend/modules/chat/chat_service.py`
Core brain of the chatbot. Handles intent detection and response logic:
- **Greeting** — returns a personalised hello using the patient's name from the DB.
- **Profile queries** — answers "what is my name/age/gender" directly from the DB.
- **Lab parameter value** — looks up the value in the cached report context and returns it directly.
- **Explanatory / general questions** — passes the question and report context to the LLM for a natural language answer.

Also manages dynamic quick-action buttons returned with each response.

---

### Link Module

#### `backend/modules/link/link_router.py`
Defines `GET /create-link` which generates a signed, time-limited report URL for a given patient ID. Also provides the `validate_signed_request` FastAPI dependency — used as authentication middleware by the chat and report routers.

#### `backend/modules/link/link_service.py`
Signs and validates HMAC-based access tokens embedded in report URLs. Tokens contain the patient hash, report ID, expiry timestamp, and a signature. Raises HTTP 401 if the token is missing, expired, or tampered with.

---

### Report Module

#### `backend/modules/report/report_router.py`
Defines `GET /api/summary`. Returns a JSON object with the patient's name, age, gender, report ID, lab reference, and status — used to populate the frontend summary card.

#### `backend/modules/report/report_service.py`
Two functions:
- `build_summary()` — fetches patient info and formats it for the summary API response.
- `load_patient_context()` — fetches all test results for a patient and formats them as a plain-text string (e.g. `hemoglobin: 13.2`) for use as LLM context.

#### `backend/modules/report/report_repository.py`
Raw SQL layer for the report module:
- `get_patient_by_hash()` — looks up a patient record by their SHA-256 hashed ID.
- `get_patient_tests()` — fetches all test parameter names and result values for a patient via a JOIN across three tables.

---

### WhatsApp Module

#### `backend/modules/whatsapp/whatsapp_router.py`
Three endpoints:
- `POST /whatsapp/send-report/{patient_id}` — manual test endpoint, sends to a hardcoded phone number.
- `POST /whatsapp/process-pending` — processes one pending notification using the old template.
- `POST /whatsapp/process-pending-new` — processes all pending notifications using the current template, returns a summary of successes and failures.

Also contains a commented-out block (dead code) from an earlier version of the batch endpoint.

#### `backend/modules/whatsapp/whatsapp_service.py`
Two functions that call the WhatsApp Cloud API (Meta Graph API):
- `send_whatsapp_template()` — sends using the old single-parameter template.
- `send_whatsapp_new_template()` — sends using `report_ready_notification_2`, which requires both a patient name and a lab name in the message body.

Both have nearly identical structure — only the template name and parameters differ.

#### `backend/modules/whatsapp/whatsapp_repository.py`
Database queries for the notification pipeline:
- `fetch_pending_notification()` — fetches one pending notification (oldest first).
- `fetch_all_pending_notifications()` — fetches all pending notifications (same query, no `LIMIT 1`).
- `update_notification_status()` — marks a notification as sent (1) or permanently failed (2).
- `increment_retry_or_fail()` — increments the retry count; permanently fails the notification after 3 attempts.

---

### Frontend

#### `frontend/index.html`
HTML shell page. The React app mounts into the `<div id="root">` element here.

#### `frontend/src/main.jsx`
React entry point. Calls `ReactDOM.createRoot()` and mounts `<App />` into the DOM.

#### `frontend/src/App.jsx`
Root component. Manages whether the chat view is open or closed. Shows the `<Summary />` card and bottom navigation buttons by default; switches to `<Chat />` when the user taps "View Summary". Handles browser back button to close chat.

#### `frontend/src/components/Summary.jsx`
Displays the patient report card. On mount, calls `GET /api/summary` with the signed URL parameters and renders the patient's name, age, gender, report ID, lab reference, and status.

#### `frontend/src/components/Chat.jsx`
Full chat UI component. Handles:
- Sending questions to `POST /chat` with the signed URL parameters.
- Displaying message history with user/bot/system styling.
- A typing indicator while waiting for the bot response.
- Dynamic quick-action buttons returned from the backend.
- A "Download Report" button shortcut.
- Disabling input while the bot is responding.

#### `frontend/src/styles.css`
All CSS styles for the application — layout, card, chat bubbles, buttons, typing indicator, etc.

#### `frontend/vite.config.js`
Vite build configuration. Likely includes a dev proxy that forwards `/chat`, `/api`, and `/whatsapp` requests to the FastAPI backend running on a different port.

#### `frontend/package.json`
Defines the frontend project metadata, npm scripts (`dev`, `build`, `preview`), and dependencies (React, Vite, etc.).

#### `frontend/package-lock.json`
Auto-generated lockfile that pins exact versions of all npm dependencies. Should not be edited manually.

#### `frontend/eslint.config.js`
ESLint configuration for the frontend. Defines linting rules for the React/JavaScript codebase.

#### `frontend/public/vite.svg`
Default Vite logo asset. Likely unused — a leftover from the Vite project scaffold.
