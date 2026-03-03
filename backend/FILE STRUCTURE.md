// link - http://127.0.0.1:8000/create-link?patientId=2

Perfect 👌
Here is a **clean, structured Markdown documentation** of your entire backend architecture and workflow.

You can copy this into:

* README.md
* Notion
* Viva notes
* Project documentation

---

# 🏥 Medical Report Chatbot Backend Architecture

## 📌 Project Purpose

This backend system:

1. Retrieves patient report data from PostgreSQL
2. Generates secure signed links for patients
3. Allows patients to view report summary
4. Enables AI chatbot to answer questions about their report
5. Uses Ollama (local LLM) for AI responses

---

# 📂 Final Folder Structure

```
backend/
│
├── main.py
│
├── core/
│   └── database.py
│
├── modules/
│   ├── chat/
│   │   ├── router.py
│   │   └── service.py
│   │
│   ├── report/
│   │   ├── router.py
│   │   ├── service.py
│   │   └── repository.py
│   │
│   ├── link/
│   │   ├── router.py
│   │   └── service.py
│   │
│   └── ai/
│       └── llm.py
│
├── shared/
│   └── cache.py
│
└── .env
```

---

# 🧠 Architecture Type

This project follows:

> **Feature-Based Modular Architecture**

Instead of:

```
routers/
services/
utils/
```

We group by business features:

```
chat/
report/
link/
ai/
```

This makes the system:

* Scalable
* Clean
* Maintainable
* Easy to understand

---

# 🔹 main.py

## 📌 Purpose

* Entry point of FastAPI app
* Registers all routers
* Adds CORS middleware

## 📌 Responsibilities

* Initialize FastAPI
* Include routers from each module
* Configure frontend access

## 📌 Workflow

```
main.py
   ↓
Registers:
   - chat router
   - report router
   - link router
```

---

# 🔹 core/database.py

## 📌 Purpose

Handles PostgreSQL connection.

## 📌 Responsibility

* Creates database connection
* Central place for DB config

## 📌 Why Separate?

Because database is infrastructure.
Other modules depend on it.

---

# 🔹 shared/cache.py

## 📌 Purpose

Stores in-memory data to improve performance.

## 📌 What It Caches

### 1️⃣ Parameter Cache

* Loads test parameter names once
* Used for detecting lab parameters in chat

### 2️⃣ Patient Context Cache

* Stores generated report text
* Avoids repeated DB fetch

### 3️⃣ Chat Memory Cache

* Stores conversation history per patient
* Enables contextual AI responses

## 📌 Important Note

This is:

* In-memory only
* Resets on server restart
* Suitable for small scale

---

# 🔹 modules/link/

## 🎯 Purpose

Handles secure access using signed URLs.

---

## link/service.py

### Responsibilities

* Hash patient ID
* Generate signed link
* Validate token signature

### Security Flow

```
patientId → SHA256 hash
           ↓
generate payload: pid|rid|exp
           ↓
sign with HMAC + SECRET
           ↓
append signature to URL
```

---

## link/router.py

### Endpoints

#### GET `/create-link`

Creates secure report link.

#### validate_signed_request()

Dependency used in other routers.

---

# 🔹 modules/report/

## 🎯 Purpose

Handles patient report data.

---

## report/repository.py

### Responsibilities

* Direct DB queries only
* No business logic

### Functions

* get_patient_by_hash()
* get_patient_tests()

---

## report/service.py

### Responsibilities

* Builds summary response
* Formats patient test results
* Converts DB data to usable structure

### Logic Separation

Repository → raw DB data
Service → business formatting

---

## report/router.py

### Endpoint

#### GET `/api/summary`

Flow:

```
Validate token
    ↓
Extract pid
    ↓
Call build_summary()
    ↓
Return patient summary JSON
```

---

# 🔹 modules/chat/

## 🎯 Purpose

Handles chatbot interactions.

---

## chat/router.py

### Endpoint

#### POST `/chat`

Flow:

```
Validate token
    ↓
Extract pid
    ↓
Call handle_chat()
```

Router contains no logic.
Only delegates to service.

---

## chat/service.py

### Responsibilities

1. Get patient ID
2. Load patient report context
3. Use cache if available
4. Build AI prompt
5. Call LLM
6. Return structured response

---

### Chat Workflow

```
User Question
      ↓
Validate Token
      ↓
Fetch Patient ID
      ↓
Check Context Cache
      ↓
If not cached → Load from DB
      ↓
Build Prompt
      ↓
Call AI (Ollama)
      ↓
Store memory
      ↓
Return answer
```

---

# 🔹 modules/ai/

## 🎯 Purpose

Handles AI integration.

---

## ai/llm.py

### Responsibilities

* Connect to Ollama
* Send structured prompt
* Parse AI response
* Manage conversation memory

### Why Separate?

So future upgrades are easy:

* Change model
* Add OpenAI
* Add streaming
* Add guardrails
* Add RAG enhancements

---

# 🔄 Complete System Workflow

---

## 1️⃣ Link Generation

```
Admin → /create-link?patientId=1
        ↓
hash patient ID
        ↓
generate signed URL
        ↓
return link
```

---

## 2️⃣ Patient Opens Link

```
Frontend opens:
  /report?pid=...&rid=...&exp=...&sig=...

Backend:
  validate signature
```

---

## 3️⃣ Load Report Summary

```
GET /api/summary
    ↓
validate token
    ↓
fetch patient data
    ↓
return summary JSON
```

---

## 4️⃣ Chat With AI

```
POST /chat
    ↓
validate token
    ↓
get patient ID
    ↓
load report context
    ↓
call Ollama
    ↓
return AI answer
```

---

# 🏗 Dependency Flow (Clean Architecture)

```
main
  ↓
router
  ↓
service
  ↓
repository
  ↓
database
```

And for AI:

```
chat.service
    ↓
ai.llm
```

No circular dependencies.

---

# 🏆 What You Achieved

You now have:

✅ Modular architecture
✅ Feature-based structure
✅ Clear separation of concerns
✅ Clean dependency flow
✅ Secure signed URL system
✅ Local LLM integration
✅ Memory caching
✅ Interview-ready backend

---

# 🧠 In Simple Words

Your backend:

* Protects patient access with signed links
* Retrieves data securely
* Converts DB records into readable report
* Uses AI to explain medical results
* Maintains conversation context
* Caches data for performance

---

If you want, I can next provide:

* 🔥 Architecture diagram (visual explanation)
* 📝 README.md ready file
* 🎤 Viva explanation script
* 🚀 Deployment guide

Tell me what you want next.
