# ⚡ Postmortem AI — Incident Response & Continuous Memory Engine

> **Autonomous Incident Postmortem & Remediation Engine** powered by persistent cross-incident retrieval via the **Hindsight Memory Engine** and **Groq LLM**.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://postmortem-ai-frontend.vercel.app/)
[![Backend Status](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://postmortem-ai-backend.onrender.com/docs)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

---

## 📌 Problem Statement

During critical enterprise outages, SRE and DevOps teams suffer from severe **organizational amnesia**:
- Recurring root causes (connection pool exhaustion, token cache OOMs, concurrency race conditions) repeat across quarters.
- Past remediation notes rot in fragmented documentation silos (Jira tickets, Google Docs, Slack channels).
- Standard baseline LLMs generate generic, non-actionable advice (e.g., "check connection strings") with zero knowledge of past institutional fixes.

**Postmortem AI** eliminates recurring downtime by correlating live incident symptoms and logs against the **Hindsight Memory Engine**, matching active alerts to past postmortems to output structured root cause analyses (RCA), timelines, 5-Whys, and verifiable preventative measures in seconds.

---

## 🧠 How Hindsight Memory is Used

Hindsight operates as the persistent intelligence layer of Postmortem AI across three primary workflows:

[ Active Outage Symptoms + Logs ]
│
▼
[ Entity & Token Extraction ]  (Component, Failure Mode, Error Tokens)
│
▼
[ Hindsight Semantic Memory Query ]
│
┌───────┴───────┐
▼               ▼
[Top-k Similar] [Zero Matches Fallback]
[Memory Nodes ] [Cold-Start Handling   ]
│
▼
[ Prompt Grounding & Synthesis via Groq ]
│
▼
[ Structured Postmortem + Memory Inspector Preview ]
│
▼
[ Continuous Learning Loop ] ──> Commits Verified Fixes back to Hindsight Bank


1. **Semantic Incident Matching:** The backend extracts failure modes, error tokens, and impacted components from raw stack traces to query Hindsight for semantically correlated past incidents.
2. **Dual-Mode Grounding Validation:** 
   - **Baseline Mode (No Memory):** Prompts the LLM without memory context to illustrate generic baseline outputs.
   - **Grounded Mode (With Hindsight):** Injects historical root-cause nodes and proven mitigation playbooks directly into the prompt context for hyper-specific RCA.
3. **Continuous Learning Loop:** When an on-call engineer reviews and confirms a fix, the resolution is committed directly back to the Hindsight Memory Bank, ensuring future outages benefit from verified institutional knowledge.

---

## 🚀 Key Features

- **⚡ Dual-Mode Memory Switch:** Toggle between baseline LLM generation and Hindsight-grounded RCA in real time.
- **🔍 Hindsight Memory Inspector:** Slide-over drawer displaying exact query vectors, extracted entities, and memory node match percentages.
- **📋 End-to-End Postmortem Generation:** Synthesizes Executive Summaries, Impact Metrics, Root Cause Analysis, 5-Whys, Timelines, and Prioritized Action Items.
- **🔄 Continuous Learning Feedback Loop:** Persists production-verified mitigations back into the long-term memory engine.
- **🗃️ Memory Bank Explorer:** Search, inspect, and filter historical incident nodes by severity and system tags.

---

## 🛠️ Architecture & Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | HTML5, TailwindCSS, JavaScript (ES6+) | Lightweight, reactive dashboard interface |
| **Frontend Hosting** | Vercel | Production CDN deployment |
| **Backend API** | FastAPI (Python 3.11), Uvicorn | High-throughput asynchronous REST API |
| **Backend Hosting** | Render | Cloud container deployment |
| **Memory Engine** | **Hindsight API** | Semantic vector storage, memory recall, and continuous persistence |
| **Inference Model** | Groq (`llama-3.3-70b-versatile`) | Postmortem structuring, reasoning, and timeline extraction |

---

## 📁 Repository Structure

```text
postmortem-ai/
├── backend/
│   ├── main.py              # FastAPI endpoints, CORS, and request routing
│   ├── memory_agent.py      # Hindsight integration, prompt grounding, and Groq inference
│   ├── requirements.txt     # Python dependencies
│   └── seed_data.py         # Seed data for historical memory bank
└── frontend/
    ├── index.html           # Postmortem studio and memory bank explorer UI
    ├── app.js               # Application controller, API integrations, and drawer logic
    └── styles.css           # Styling rules and responsive layouts
