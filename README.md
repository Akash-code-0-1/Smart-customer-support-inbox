# Smart Customer Support Inbox API

A concurrent, real-time support agent dashboard built to handle high-volume ticket pipelines, prevent agent race conditions via Redis locks, and parse message inputs asynchronously.

## 📦 System Architecture & Requirements

* **Backend:** Python / Django 5.x / Django REST Framework
* **Frontend:** Next.js 14+ (App Router) / TailwindCSS / TanStack React Query
* **Data & Brokerage Layers:** Redis (Caching, Locking, Event Buffer) & SQLite3 (Relational Storage)
* **Task Queue:** Celery 5.x

---

## 🛠️ Local Machine Setup

### 1. Redis Environment

Start an isolated Redis container instance bound to standard ports:

```bash
docker run -d --name inbox-redis -p 6379:6379 redis:alpine

```

### 2. Django Backend Installation

Navigate to your backend directory, initialize your virtual environment, and install base packages:

```bash
cd backend/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

Run structural migrations, seed core relational models, and launch the development service runner:

```bash
python3 manage.py migrate
python3 manage.py runserver

```

### 3. Asynchronous Worker Instance

Open a separate shell terminal, enter your backend environment, and boot your Celery background queue handler:

```bash
source venv/bin/activate
celery -A config worker --loglevel=info

```

### 4. Next.js Frontend Deployment

Open a separate shell terminal, install package dependencies, and run the client-side single-page layout:

```bash
cd frontend/
npm install
npm run dev

```

The application web user interface is now accessible locally via: `http://localhost:3000/`

---

## Grading & Evaluation Runbook

Follow these sequential steps to test each requirement component of the task criteria directly:

### Interactive System Documentation (OpenAPI 3.0)

* Open your browser to **`http://localhost:8000/api/docs/`** to pull up the automated Swagger UI portal.
* Verify structural routes, schemas, and parameter criteria configurations.
* Click **Authorize** to bind an active JWT access key token string (`Bearer <access_token>`) to execute test operations directly against live API endpoints inside the browser.

#### 🖼️ Working Proof (Swagger Dashboard View)
![OpenAPI Swagger Documentation Interface](screenshots/swagger-docs.png)
---

### State Concurrency & Race Condition Elimination

* Authenticate as a support agent and select any active conversation thread in the Next.js interface.
* The system assigns a distinct thread lock key inside Redis, reserving the workspace for the authenticated profile (`admin@test.com`).
* Open a private incognito session or an alternate browser tab using a separate agent profile access key. The second agent will see that the text composition canvas is strictly deactivated, showing: **`🔒 Handled by admin@test.com`**.

#### 🖼️ Working Proof (Session Locking Banner View)

![Active Multi-Agent Concurrency Session Lock](https://github.com/Akash-code-0-1/Smart-customer-support-inbox/blob/main/screenshots/ui.png?raw=true)

---

### 🤖 Part 3: Quick Macro Menu

* Inside the composition zone of any active ticket, click the floating circular blue node button featuring the **`🤖`** element.
* This expands an integrated panel containing **5 pre-made professional support response scripts** (Greetings, Refund, Shipping, Replacement, and Account Cancellation).
* Click any macro list option: the system closes the selection tree instantly and transfers the full text block parameter down to the primary message input block for prompt agent modification or fast transmission.

#### 🖼️ Working Proof (AI Macros Action Interface)
![AI Floating Macro Selection Speed Dial Menu](https://github.com/Akash-code-0-1/Smart-customer-support-inbox/blob/main/screenshots/tmsg.png?raw=true)
---

### 📡 Part 4: Live Server-Sent Events (SSE) & Async Verification

To test live data ingestion without a manual page refresh, fire a mockup customer message payload into your SQLite environment using a raw `curl` execution terminal request:

```bash
curl -X POST http://localhost:8000/api/conversations/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_ACCESS_TOKEN" \
  -d '{"sender": "customer", "message": "Can I please get a refund for this broken item?"}'

```

![](https://github.com/Akash-code-0-1/Smart-customer-support-inbox/blob/main/screenshots/terminal-req.png?raw=true)

![](https://github.com/Akash-code-0-1/Smart-customer-support-inbox/blob/main/screenshots/req-output.png?raw=true)

#### Expected Evaluation Behavior:

1. **The Streaming Layer:** The new incoming message automatically injects straight into the active Next.js interface loop array without page drops or manual reloads.
2. **The Worker Pipeline:** The running Celery terminal logs a successful background message execution event loop, reads the incoming customer string parameters, evaluates text weights, and writes the resulting structural metadata updates back to the SQLite row container cleanly.
