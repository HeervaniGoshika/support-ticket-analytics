# 🤖 Support Intelligence AI

### LLM-Powered Customer Support Analytics & Anomaly Detection System

<p align="center">
  <b>Natural Language Analytics • LLM • Anomaly Detection • FastAPI • Streamlit • Docker</b>
</p>

---

## 🌟 Overview

**Support Intelligence AI** is an end-to-end AI-powered customer support analytics platform that transforms support ticket data into actionable insights through **Natural Language Querying, LLM-based intent understanding, anomaly detection, REST APIs, and an interactive Streamlit dashboard**.

Instead of writing SQL queries, users can ask questions such as:

> **"How many critical tickets are unresolved?"**

The system uses an LLM to understand the question, converts it into a **validated structured query plan**, executes the appropriate backend operation, and returns the result through the REST API and Streamlit interface.

This project was developed as part of the **DOTMappers AI Engineer Technical Assessment**.

---

# ✨ Key Features

### 🧠 Natural Language Analytics

Ask questions about customer support tickets using natural language.

Examples:

- How many tickets are currently open?
- Which agent resolved the most tickets this month?
- What is the average customer rating for Technical tickets?
- Show me all Critical tickets.
- How many High priority tickets are unresolved?

### 🤖 LLM-Powered Query Understanding

The system uses a locally running **Ollama LLM** to transform natural-language questions into structured intents.

```text
Natural Language Question
            ↓
         Ollama LLM
            ↓
     Structured Query Plan
            ↓
       Validation Layer
            ↓
       Query Service
            ↓
          SQLite
            ↓
      Actual Data Result
```

The LLM handles **natural-language understanding**, while Python and SQLAlchemy perform the actual computation.

### 🔐 Safe Query Architecture

The LLM does **not** execute arbitrary SQL.

Supported analytical operations include:

```text
count_tickets
agent_resolution_count
average_customer_rating
list_tickets
anomaly_check
```

Example:

```json
{
  "intent": "count_tickets",
  "filters": {
    "priority": "Critical",
    "status": "Open"
  }
}
```

The backend validates the plan before executing the corresponding database operation.

### 🚨 Intelligent Anomaly Detection

The system combines **business rules** and **Isolation Forest**.

#### Business Rule Detection

```text
Priority = High / Critical
        +
Status = Open / Escalated
        +
Age > 24 hours
        ↓
     🚨 Anomaly
```

#### Statistical Detection

```text
Resolution Time
       ↓
Isolation Forest
       ↓
Unusual Observations
       ↓
Anomaly Report
```

### ⚡ REST API

Built with **FastAPI** and automatic Swagger/OpenAPI documentation.

```text
GET  /health
POST /query
GET  /anomalies
GET  /
```

### 📊 Interactive Dashboard

The Streamlit UI provides:

- Natural-language query input
- AI-generated answers
- Detected query intent
- Query result tables
- Anomaly detection
- Configurable anomaly threshold
- API connectivity status
- Example questions

### 🗄️ Queryable Data Layer

```text
support_tickets.csv
        ↓
   Data Validation
        ↓
      Pandas
        ↓
    SQLAlchemy
        ↓
       SQLite
```

### 🐳 Dockerized Deployment

Start the complete system with:

```bash
docker compose up --build
```

The setup includes FastAPI, Streamlit, Ollama, the local LLM model, and SQLite.

### 🧪 Automated Testing

Tests cover query functionality, rating calculations, agent analytics, anomaly detection, API endpoints, and health checks.

```bash
pytest -v
```

---

# 🏗️ System Architecture

```text
                         ┌───────────────────────┐
                         │      User / UI        │
                         │      Streamlit        │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       FastAPI         │
                         │                       │
                         │  /query               │
                         │  /anomalies           │
                         │  /health              │
                         └───────────┬───────────┘
                                     │
                     ┌───────────────┴───────────────┐
                     │                               │
                     ▼                               ▼
          ┌─────────────────────┐         ┌─────────────────────┐
          │    Query Service    │         │  Anomaly Service    │
          └──────────┬──────────┘         └──────────┬──────────┘
                     │                               │
                     ▼                               ▼
          ┌─────────────────────┐         ┌─────────────────────┐
          │   Query Execution   │         │ Business Rules +   │
          │                     │         │ Isolation Forest    │
          └──────────┬──────────┘         └─────────────────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │       SQLite        │
          │     Ticket Data     │
          └──────────▲──────────┘
                     │
          ┌──────────┴──────────┐
          │   CSV Ingestion     │
          │  Validation Layer   │
          └─────────────────────┘

                    LLM Layer
                       │
                       ▼
              ┌─────────────────┐
              │     Ollama      │
              │   llama3.2:3b   │
              └────────┬────────┘
                       │
                       ▼
             Natural Language
              → Structured Intent
```

---

# 🔄 Query Processing Pipeline

```text
User Question
      ↓
Natural Language Understanding
      ↓
Ollama LLM
      ↓
Structured JSON Query Plan
      ↓
Intent Validation
      ↓
Query Service
      ↓
SQLAlchemy
      ↓
SQLite
      ↓
Deterministic Result
      ↓
FastAPI Response
      ↓
Streamlit Visualization
```

### Example

User:

```text
Which agent resolved the most tickets this month?
```

LLM output:

```json
{
  "intent": "agent_resolution_count",
  "filters": {
    "period": "month"
  }
}
```

The backend validates the intent, queries SQLite, groups resolved tickets by agent, and returns the result.

**LLM = question understanding. Backend = data computation.**

---

# 🚨 Anomaly Detection Pipeline

```text
                 Ticket Dataset
                       │
                       ▼
              ┌─────────────────┐
              │ Anomaly Engine  │
              └────────┬────────┘
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
      Business Rules       Isolation Forest
             │                   │
             ▼                   ▼
   Unresolved High/       Unusual Resolution
   Critical Tickets            Times
             │                   │
             └─────────┬─────────┘
                       ▼
               Combined Anomalies
                       │
                       ▼
                 REST API / UI
```

---

# 📦 Dataset

The project uses the provided:

```text
support_tickets.csv
```

The assessment dataset contains **500 support tickets**.

| Column | Description |
|---|---|
| `ticket_id` | Unique ticket identifier |
| `created_at` | Ticket creation timestamp |
| `category` | Billing / Technical / General |
| `priority` | Low / Medium / High / Critical |
| `status` | Open / Resolved / Escalated |
| `response_time_hrs` | Time until first agent response |
| `resolution_time_hrs` | Time until resolution |
| `agent_id` | Assigned support agent |
| `customer_rating` | Customer satisfaction rating |
| `issue_summary` | Short description of the issue |

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Language | Python |
| API | FastAPI |
| LLM | Ollama |
| LLM Model | Llama 3.2 3B |
| Data Processing | Pandas, NumPy |
| Database | SQLite |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Anomaly Detection | Scikit-learn / Isolation Forest |
| UI | Streamlit |
| HTTP Client | HTTPX / Requests |
| Testing | Pytest |
| Containerization | Docker |
| Orchestration | Docker Compose |

---

# 📁 Project Structure

```text
dotmappers-ai-assessment/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── query.py
│   │   ├── anomalies.py
│   │   └── health.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ingestion.py
│   │   ├── query_service.py
│   │   ├── anomaly_service.py
│   │   └── llm_service.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── validators.py
│
├── ui/
│   └── streamlit_app.py
│
├── data/
│   └── support_tickets.csv
│
├── tests/
│   ├── test_query.py
│   ├── test_anomalies.py
│   └── test_api.py
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

### Local execution

- Python 3.11+
- Ollama
- Git

### Docker execution

- Docker
- Docker Compose

---

# ⚙️ Local Installation

## 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/dotmappers-ai-assessment.git
cd dotmappers-ai-assessment
```

Replace `YOUR_USERNAME` with your GitHub username.

## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Ollama

Install Ollama and start the Ollama service.

Pull the required model:

```bash
ollama pull llama3.2:3b
```

Verify:

```bash
ollama list
```

## 5. Start FastAPI

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

## 6. Start Streamlit

Open another terminal:

```bash
streamlit run ui/streamlit_app.py
```

Open:

```text
http://localhost:8501
```

---

# 🐳 Docker Deployment

Recommended:

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| FastAPI | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Streamlit | http://localhost:8501 |
| Ollama | http://localhost:11434 |

Stop:

```bash
docker compose down
```

Remove containers and volumes:

```bash
docker compose down -v
```

> The first Docker startup may take additional time because the Ollama model needs to be downloaded.

---

# 🔌 REST API

## Health Check

```http
GET /health
```

Example:

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "healthy",
  "service": "DOTMappers AI Support Intelligence",
  "version": "1.0.0",
  "database": "healthy",
  "llm": "llama3.2:3b"
}
```

## Natural Language Query

```http
POST /query
```

Request:

```json
{
  "question": "How many critical tickets are unresolved?"
}
```

Response structure:

```json
{
  "question": "How many critical tickets are unresolved?",
  "intent": "count_tickets",
  "answer": "There are X tickets matching the requested criteria.",
  "data": [
    {
      "count": "X"
    }
  ]
}
```

## Anomaly Detection

```http
GET /anomalies
```

Default unresolved-ticket threshold:

```text
24 hours
```

Custom threshold:

```http
GET /anomalies?age_hours=12
```

---

# 💬 Example Natural Language Queries

### Ticket Counts

```text
How many tickets are currently open?
```

```text
How many critical tickets are unresolved?
```

```text
How many Technical tickets are there?
```

### Agent Analytics

```text
Which agent resolved the most tickets this month?
```

```text
Show the resolved ticket count by agent.
```

### Customer Satisfaction

```text
What is the average customer rating for Technical category tickets?
```

```text
What is the average customer rating for Billing tickets?
```

### Ticket Filtering

```text
Show me all Critical tickets.
```

```text
Show unresolved High priority tickets.
```

```text
Show all Critical tickets not resolved within 12 hours.
```

### Time-Based Analytics

```text
Which agent resolved the most tickets this month?
```

```text
Are there any anomalies in resolution times this week?
```

---

# 🧠 LLM Design

A key architectural decision is that the LLM acts as a **semantic interpretation layer**, not as the database itself.

### ❌ Direct LLM → SQL

```text
User
 ↓
LLM
 ↓
Generated SQL
 ↓
Database
```

Potential problems:

- Invalid SQL
- Hallucinated fields
- Unexpected operations
- Security risks
- Incorrect analytical results

### ✅ Structured Query Architecture

```text
User
 ↓
LLM
 ↓
Structured Intent
 ↓
Validation
 ↓
Known Query Function
 ↓
SQLAlchemy
 ↓
SQLite
```

This approach keeps numerical analytics deterministic.

---

# 🛡️ Data Validation

Before ingestion, the CSV is validated for:

- Required columns
- Duplicate ticket IDs
- Timestamp parsing
- Numeric fields
- Allowed categories
- Allowed priorities
- Allowed statuses
- Customer rating range
- Missing values

---

# 🗄️ Database Design

The `Ticket` model contains:

```text
Ticket
 ├── ticket_id
 ├── created_at
 ├── category
 ├── priority
 ├── status
 ├── response_time_hrs
 ├── resolution_time_hrs
 ├── agent_id
 ├── customer_rating
 └── issue_summary
```

Indexes are applied to frequently queried fields such as:

```text
ticket_id
created_at
category
priority
status
agent_id
```

---

# 📊 UI Workflow

## Natural Language Analytics

```text
Enter Question
      ↓
Click "Ask AI"
      ↓
LLM interprets question
      ↓
Backend executes query
      ↓
Display answer
      ↓
Display structured results
```

## Anomaly Detection

```text
Select Age Threshold
        ↓
Detect Anomalies
        ↓
Business Rule Detection
        +
Isolation Forest
        ↓
Display anomaly count
        ↓
Display anomaly details
```

---

# 🧪 Testing

Run:

```bash
pytest -v
```

Tests include:

```text
tests/
│
├── test_query.py
│   ├── Ticket counting
│   ├── Average ratings
│   └── Agent resolution counts
│
├── test_anomalies.py
│   └── Old unresolved ticket detection
│
└── test_api.py
    ├── Root endpoint
    └── Health endpoint
```

---

# 🧩 Design Decisions

## Why FastAPI?

- Type-safe request validation
- Automatic OpenAPI documentation
- Dependency injection
- Clean Python integration

## Why SQLite?

- Small assessment-scale dataset
- No external database server
- Zero-cost setup
- Simple evaluator experience
- Straightforward migration path to PostgreSQL

## Why SQLAlchemy?

- Separates database operations from API code
- Reusable query logic
- ORM-based data access
- Database abstraction

## Why Ollama?

- Local LLM inference
- No paid API required
- Zero-cost evaluation
- Keeps support-ticket processing local

## Why Isolation Forest?

The dataset does not provide labelled anomaly examples. Isolation Forest provides an unsupervised approach for identifying unusual numerical observations such as resolution times.

## Why Streamlit?

Streamlit provides a lightweight interface for demonstrating backend functionality without introducing a separate frontend framework.

---

# 🔐 Reliability & Safety

The system uses:

### Structured LLM Output

The LLM is instructed to return a predefined JSON structure.

### Intent Validation

Only supported intents are accepted.

### Controlled Query Execution

The LLM cannot execute arbitrary SQL.

### Data Validation

Incoming data is validated before ingestion.

### Deterministic Analytics

Numerical results are calculated by Python/SQL rather than generated by the LLM.

### Error Handling

The API handles:

- Invalid questions
- LLM failures
- Database failures
- Invalid input
- Missing data

---

# 📈 Scalability

The current architecture is intentionally lightweight for the assessment environment.

A production evolution could look like:

```text
                     Load Balancer
                           │
                           ▼
                 ┌───────────────────┐
                 │   FastAPI Cluster  │
                 └─────────┬─────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
           Redis       PostgreSQL    LLM Gateway
           Cache          DB             │
              │                         │
              │                         ▼
              │                    Model Serving
              │
              ▼
       Background Workers
              │
              ▼
       Streaming / Batch Data
```

Potential production improvements:

- PostgreSQL instead of SQLite
- Redis caching
- Background ingestion workers
- Message queues
- Horizontal FastAPI scaling
- Dedicated LLM inference service
- Authentication and authorization
- API rate limiting
- Observability and monitoring
- CI/CD pipelines
- Container orchestration
- Model evaluation and monitoring

---

# 🔮 Future Improvements

### 🤖 Advanced AI

- Semantic search over `issue_summary`
- Embedding-based ticket similarity
- Retrieval-Augmented Generation
- Automatic ticket summarization
- Ticket classification
- Suggested resolutions
- Agent assistance
- Conversational multi-turn analytics

### 📊 Analytics

- Agent performance dashboards
- SLA monitoring
- Category trends
- Priority distribution
- Resolution-time trends
- Customer satisfaction trends

### 🚨 Anomaly Detection

- Adaptive thresholds
- Time-series anomaly detection
- Category-specific anomaly models
- Agent-level anomaly detection
- SLA violation prediction

### 🏭 Productionization

- PostgreSQL
- Redis
- Authentication
- Role-based access control
- CI/CD
- Monitoring
- Distributed inference
- Kubernetes

---

# ⚠️ Known Limitations

1. The LLM currently operates over a predefined set of analytical intents.
2. Arbitrary SQL generation is intentionally not supported.
3. SQLite is suitable for this assessment but would be replaced with PostgreSQL for production-scale workloads.
4. Local LLM inference performance depends on available CPU/GPU resources.
5. Isolation Forest thresholds may require calibration using real historical production data.
6. Relative time expressions such as "this week" and "this month" are interpreted relative to the available dataset.
7. The current anomaly engine focuses primarily on resolution-time anomalies and unresolved high-priority tickets.

---

# 📋 Assessment Requirements Coverage

| Requirement | Implementation |
|---|---|
| CSV ingestion | Pandas + validation + SQLite |
| Queryable data | SQLite + SQLAlchemy |
| Natural language questions | Ollama LLM |
| LLM requirement | Structured intent extraction |
| Anomaly detection | Business rules + Isolation Forest |
| REST API | FastAPI |
| Minimal UI | Streamlit |
| Health endpoint | `GET /health` |
| Query endpoint | `POST /query` |
| Anomaly endpoint | `GET /anomalies` |
| Testing | Pytest |
| Containerization | Docker + Docker Compose |
| Documentation | README |

---

# 📁 Configuration

Configuration is managed through environment variables.

Example:

```env
APP_NAME=DOTMappers AI Support Intelligence
APP_VERSION=1.0.0

DATABASE_URL=sqlite:///./data/support_tickets.db

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

API_HOST=0.0.0.0
API_PORT=8000

UNRESOLVED_AGE_HOURS=24
ISOLATION_CONTAMINATION=0.05
```

Copy `.env.example` to `.env` and adjust values if required.

---

# 🗺️ Development Roadmap

```text
Phase 1
✓ Dataset validation
✓ CSV ingestion
✓ SQLite persistence

Phase 2
✓ Natural language query understanding
✓ Structured LLM output
✓ Query execution

Phase 3
✓ Business-rule anomaly detection
✓ Isolation Forest

Phase 4
✓ FastAPI
✓ Streamlit UI

Phase 5
✓ Testing
✓ Docker
✓ Documentation

Future
○ PostgreSQL
○ Redis
○ RAG
○ Advanced anomaly detection
○ Authentication
○ Observability
○ CI/CD
```

---

# 💡 Engineering Principles

```text
Separation of Concerns
        +
Modular Architecture
        +
Validated LLM Output
        +
Deterministic Data Processing
        +
Controlled Query Execution
        +
Testability
        +
Containerized Deployment
```

The goal is not simply to demonstrate an LLM call, but to demonstrate how an LLM can be integrated into a reliable software system.

---
