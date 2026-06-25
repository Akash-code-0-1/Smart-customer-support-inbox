# Smart Customer Support Inbox

A real-time customer support portal built with Django, Django REST Framework (DRF), and Next.js (App Router). The platform features an optimistic UI with rollback capabilities, concurrent thread locking, keyword-driven AI response templates, and an asynchronous processing pipeline for text sentiment analysis.

---

## 🏗️ Architectural Decisions & Trade-offs

### Real-Time Pipeline: Server-Sent Events (SSE) vs. WebSockets
For streaming message updates and lock state transitions to the agent interface, **Server-Sent Events (SSE)** were selected over bidirectional WebSockets:
* **Resource Efficiency:** Support agents primarily consume streaming event updates. Outbound mutations (agent replies) are handled via standard HTTP POST requests, making the overhead of a permanent full-duplex WebSocket connection unnecessary.
* **Resilience:** SSE includes native client-side reconnection handling out of the box, simplifying the frontend state synchronization layer.
* **Auth Bypass Solution:** Addressed the technical limitation where browser `EventSource` engines cannot pass custom headers (like JWT Bearer tokens) by engineering an inline query-parameter authorization verification architecture.

### Asynchronous Sentiment Analysis Engine
To maintain sub-100ms response cycles, text sentiment analysis is completely decoupled from the synchronous request-response lifecycle. When an agent submits a message, the request resolves immediately, and a background task is dispatched via a **Redis broker** to standalone **Celery daemon workers** to process and save the conversation's sentiment state.

---

## 🚀 Local Deployment Guide

### 1. Prerequisites (Infrastructure Layer)
Spin up the decoupled Redis broker container via Docker:
```bash
docker run -d --name redis-broker -p 6379:6379 redis


2. Backend Installation & API Startup
Navigate to the backend directory, activate the virtual environment, migrate the database schemas, seed the default admin profile, and start the development server:

cd backend
source venv/bin/activate

# Apply structural migrations
python3 manage.py migrate

# Boot the API server
python3 manage.py runserver 8000


3. Asynchronous Task Processor Startup
Open a new terminal tab, navigate to the backend, and activate the Celery worker pool:

cd backend
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings
celery -A config worker --loglevel=info


4. Frontend Workspace Setup
Open a separate terminal window, navigate to the frontend directory, install dependencies, and run the Next.js development server:

cd frontend
npm install
npm run dev


Open your browser and navigate to: http://localhost:3000/inbox/1


Automated Testing Protocol
To verify data structures, concurrency locks, and background tasks independently, execute the automated backend test runner:

cd backend
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings
python3 manage.py test core