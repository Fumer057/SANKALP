# SANKALP — AI 3D Visualization System

SANKALP is an intelligent full-stack system that retrieves, validates, and presents 3D visual representations of any concept. It uses a robust 5-stage pipeline to find high-quality 3D models from the web, with an automated AI generation fallback.

## 🚀 Key Features

*   **Intelligent 5-Stage Pipeline**: Orchestrates Query Expansion, Local Retrieval, AI Validation, Web Scraping, and AI Generation.
*   **Semantic Web Scraper**: Searches a curated catalog of 30+ verified free GLB models from Khronos Group, Google Model Viewer, and Three.js CDNs.
*   **AI Validation**: Automatically scores retrieved models for semantic relevance to ensure the best visual match.
*   **Interactive 3D Viewer**: Built with React Three Fiber and Drei, featuring HDRI environment lighting and smooth orbit controls.
*   **Model Gallery**: A dedicated space to browse all retrieved and generated models cached by the system.
*   **Deployment Ready**: Optimized with Docker for backend hosting and Vercel-ready frontend configuration.

## 🛠️ Tech Stack

*   **Frontend**: Next.js, React, Three.js, React Three Fiber, Tailwind CSS, Framer Motion.
*   **Backend**: FastAPI (Python), httpx, Pydantic.
*   **AI Models**: Shap-E (via Hugging Face) for 3D generation.

## 🏗️ The 5-Stage Pipeline

1.  **Query Processing**: Semantic expansion of user input using LLMs.
2.  **Local DB Retrieval**: Lightning-fast lookup of pre-cached local models.
3.  **AI Validation**: Scoring candidates to ensure they meet a confidence threshold.
4.  **Live Web Search**: Downloading and caching real 3D models from public CDNs.
5.  **AI Generation**: Generating a unique model from scratch as a final fallback.

## 📥 Installation

### Prerequisites
*   Node.js (v18+)
*   Python 3.10+

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn main:app --port 8001
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The app will be available at `http://localhost:3000`.

## 🚢 Deployment

The project includes a `Dockerfile` in the backend directory for easy deployment to platforms like Render, Railway, or Google Cloud Run. The frontend is ready for Vercel out of the box.

---
*Created with ❤️ for AI-powered 3D exploration.*
