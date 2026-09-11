# SANKALP — AI 3D Visualization System

SANKALP is an intelligent full-stack system designed to retrieve, validate, and render 3D visual representations of concepts and physical objects. The platform integrates semantic search, curated asset ingestion, automated validation scoring, and AI-driven generative fallback to deliver real-time interactive 3D experiences.

---

## Overview

Finding accurate 3D assets for educational, simulation, and visualization purposes often requires manual searching across disconnected repositories. SANKALP automates this workflow through a structured 5-stage retrieval and generation pipeline. When high-confidence assets are unavailable in local or public 3D registries, the system seamlessly transitions to generative AI models to construct 3D representations on demand.

---

## Key Features

- **Multi-Stage Asset Pipeline**: Orchestrates query expansion, local cache lookup, semantic validation, web ingestion, and generative fallback.
- **Automated Validation and Scoring**: Evaluates candidate 3D models against semantic relevance metrics to ensure contextual accuracy before rendering.
- **Interactive 3D Viewport**: Built on Three.js, React Three Fiber, and Drei, offering orbit controls, dynamic lighting, and environment mapping.
- **Multi-Source Ingestion**: Capable of querying curated catalogs, Sketchfab, Google Model Viewer, and Three.js public repositories.
- **Model Gallery and Caching**: SQLite-backed caching and static asset storage for fast retrieval and offline availability.
- **Containerized Architecture**: Docker-ready backend service paired with a Vercel-optimized Next.js frontend.

---

## The 5-Stage Pipeline

```
[ User Input Query ]
         │
         ▼
[ Stage 1: Query Expansion ] ──────► (LLM-based entity extraction & semantic expansion)
         │
         ▼
[ Stage 2: Local & Global Retrieval ] ──► (Local SQLite cache, Sketchfab API, public CDNs)
         │
         ▼
[ Stage 3: Semantic AI Validation ] ──► (Confidence scoring against relevance threshold)
         │
         ├───► [ Match >= Threshold ] ──► [ Stage 4: Asset Selection & Delivery ]
         │
         └───► [ Match < Threshold  ] ──► [ Stage 5: Shap-E AI Generation Fallback ]
```

1. **Query Expansion**: Analyzes natural language input to extract core entities, category tags, and descriptive visual properties.
2. **Catalog and Web Retrieval**: Queries pre-indexed local models, SQLite cache entries, and verified online GLB repositories (including Sketchfab and public CDNs).
3. **AI Validation Scoring**: Analyzes candidate metadata against the query profile, calculating a normalized confidence score (0–100%).
4. **Asset Selection**: Serves verified GLB models directly when candidate confidence satisfies the configured threshold.
5. **Generative Fallback**: Automatically invokes OpenAI Shap-E to synthesize a 3D GLB model from scratch when no pre-existing candidate satisfies quality requirements.

---

## Tech Stack

### Frontend
- **Framework**: Next.js 16, React 19
- **3D Graphics**: Three.js, React Three Fiber (`@react-three/fiber`), Drei (`@react-three/drei`)
- **Styling and Motion**: Tailwind CSS, Framer Motion
- **Language**: TypeScript

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Server**: Uvicorn (ASGI)
- **HTTP Client**: HTTPX
- **Data Validation**: Pydantic
- **Storage**: SQLite and Local Static File Serving

### AI and 3D Synthesis
- **Generative 3D**: Hugging Face Shap-E
- **Entity Processing**: OpenAI / Language Models

---

## Project Structure

```
SANKALP/
├── backend/
│   ├── services/
│   │   ├── database.py         # SQLite cache and session management
│   │   ├── fallback.py         # AI 3D generation fallback (Shap-E)
│   │   ├── query_processor.py  # Entity extraction and semantic expansion
│   │   ├── retrieval.py        # Model indexing and API retrieval
│   │   ├── validator.py        # Relevance scoring and confidence evaluation
│   │   └── web_scraper.py      # Multi-source web ingestion service
│   ├── static/                 # Static GLB models and cached assets
│   ├── config.py               # Application configuration and thresholds
│   ├── Dockerfile              # Backend container configuration
│   ├── main.py                 # FastAPI application entrypoint
│   ├── requirements.txt        # Python package dependencies
│   └── routes.py               # REST API endpoints
├── frontend/
│   ├── src/                    # UI components, 3D viewport, and pages
│   ├── package.json            # Node.js dependencies and scripts
│   ├── tailwind.config.ts      # Tailwind CSS styling configuration
│   └── tsconfig.json           # TypeScript configuration
└── README.md
```

---

## Installation & Setup

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- Git

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # On macOS/Linux:
   python -m venv venv
   source venv/bin/activate

   # On Windows:
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables (optional):
   Create a `.env` file in the `backend/` directory:
   ```env
   SKETCHFAB_API_KEY=your_sketchfab_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

5. Start the backend server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```
   The backend API will be available at `http://localhost:8001`.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The application will be accessible at `http://localhost:3000`.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service status and endpoint discovery |
| `GET` | `/docs` | Interactive OpenAPI / Swagger documentation |
| `GET` | `/api/search?q={query}&force_generate={bool}` | Executes the 5-stage retrieval pipeline |
| `GET` | `/api/gallery` | Returns indexed local and cached 3D assets |

---

## Deployment

### Backend (Docker)
A production-ready `Dockerfile` is included in the backend directory:
```bash
cd backend
docker build -t sankalp-backend .
docker run -p 8001:8001 sankalp-backend
```

### Frontend (Vercel)
The Next.js frontend is configured for deployment on Vercel:
1. Connect your repository to Vercel.
2. Specify `frontend` as the Root Directory.
3. Deploy with default Next.js build settings.

---

## License

This project is licensed under the MIT License.
