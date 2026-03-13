'use client';

import { useState, FormEvent } from 'react';
import dynamic from 'next/dynamic';
import PipelineStatus from '@/components/PipelineStatus';
import ModelInfo from '@/components/ModelInfo';

// Dynamically import ModelViewer with SSR disabled (Three.js needs browser APIs)
const ModelViewer = dynamic(() => import('@/components/ModelViewer'), {
  ssr: false,
  loading: () => (
    <div className="loading-container">
      <div className="loading-spinner" />
      <div className="loading-text">Initializing 3D Engine...</div>
    </div>
  ),
});

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001';

const QUICK_SEARCHES = [
  'Human Heart',
  'Brain Anatomy',
  'DNA Molecule',
  'Solar System',
  'Robot',
  'Car Engine',
];

interface SearchResult {
  status: string;
  query: string;
  search_profile: Record<string, unknown>;
  pipeline_stages: Array<{
    stage: number;
    name: string;
    status: string;
    detail: string;
  }>;
  best_model: {
    id: string;
    name: string;
    url: string;
    description: string;
    source: string;
    poly_count?: number;
    file_size_mb?: number;
    confidence_score: number;
    validation_explanation: string;
    is_fallback?: boolean;
    category?: string;
    tags?: string[];
  } | null;
  all_candidates: Array<{
    id: string;
    name: string;
    url: string;
    source: string;
    confidence_score: number;
  }>;
  is_fallback: boolean;
}

type AppState = 'idle' | 'searching' | 'results' | 'error';

export default function Home() {
  const [query, setQuery] = useState('');
  const [appState, setAppState] = useState<AppState>('idle');
  const [result, setResult] = useState<SearchResult | null>(null);
  const [selectedModelUrl, setSelectedModelUrl] = useState('');
  const [error, setError] = useState('');
  const [currentStage, setCurrentStage] = useState(0);

  const handleSearch = async (searchQuery?: string) => {
    const q = searchQuery || query;
    if (!q.trim()) return;

    setAppState('searching');
    setResult(null);
    setError('');
    setCurrentStage(1);

    // Simulate pipeline stages for visual effect
    const stageDelays = [600, 1200, 1800];
    stageDelays.forEach((delay, idx) => {
      setTimeout(() => setCurrentStage(idx + 2), delay);
    });

    try {
      const response = await fetch(`${BACKEND_URL}/api/search?q=${encodeURIComponent(q)}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Server error: ${response.status}`);

      const data: SearchResult = await response.json();
      setResult(data);
      setSelectedModelUrl(data.best_model?.url || '');
      setCurrentStage(data.pipeline_stages.length);
      setAppState('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect to the backend server.');
      setAppState('error');
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    handleSearch();
  };

  const handleQuickSearch = (tag: string) => {
    setQuery(tag);
    handleSearch(tag);
  };

  return (
    <div className="app-container">

      <main className="main-content">
        {/* Search Section */}
        <section className="search-section">
          <h1 className="search-title">
            Visualize Any Concept<br />in 3D
          </h1>
          <p className="search-subtitle">
            Type any concept — our AI pipeline retrieves, validates, and presents
            the best 3D model with intelligent fallback generation.
          </p>
          <form onSubmit={handleSubmit} className="search-bar-wrapper">
            <input
              id="search-input"
              className="search-bar"
              type="text"
              placeholder='Try "Human Heart", "DNA Molecule", "Solar System"...'
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={appState === 'searching'}
            />
            <button
              id="search-button"
              className="search-btn"
              type="submit"
              disabled={appState === 'searching' || !query.trim()}
              aria-label="Search"
            >
              {appState === 'searching' ? '⟳' : '→'}
            </button>
          </form>
          <div className="quick-tags">
            {QUICK_SEARCHES.map((tag) => (
              <button
                key={tag}
                className="quick-tag"
                onClick={() => handleQuickSearch(tag)}
                disabled={appState === 'searching'}
              >
                {tag}
              </button>
            ))}
          </div>
        </section>

        {/* Pipeline Status — shown during search and results */}
        {(appState === 'searching' || appState === 'results') && result?.pipeline_stages && (
          <PipelineStatus stages={result.pipeline_stages} currentStage={currentStage} />
        )}

        {/* Loading State */}
        {appState === 'searching' && (
          <div className="loading-container animate-fade-in-up">
            <div className="loading-spinner" />
            <div className="loading-text">Processing your query through the AI pipeline...</div>
            <div className="loading-subtext">
              Expanding semantics → Retrieving models → Validating with AI → Selecting best match
            </div>
          </div>
        )}

        {/* Error State */}
        {appState === 'error' && (
          <div className="empty-state animate-fade-in-up">
            <div className="empty-icon">⚠️</div>
            <div className="empty-title">Connection Error</div>
            <div className="empty-description">
              {error}
              <br /><br />
              Make sure the backend server is running:
              <br />
              <code style={{ color: '#6C63FF' }}>
                python -m uvicorn main:app --reload
              </code>
            </div>
          </div>
        )}

        {/* Results */}
        {appState === 'results' && result?.best_model && (
          <div className="results-section animate-fade-in-up">
            {/* 3D Viewer */}
            <div className="viewer-container">
              <div className="viewer-overlay-top">
                <span
                  className={`viewer-badge ${result.is_fallback ? 'fallback' : 'success'}`}
                >
                  {result.is_fallback ? '🤖 AI Generated (Fallback)' : '✓ Retrieved Model'}
                </span>
                <div className="viewer-controls">
                  <button className="viewer-control-btn" title="Reset View" aria-label="Reset View">
                    ↻
                  </button>
                </div>
              </div>

              <ModelViewer modelUrl={selectedModelUrl} autoRotate={true} />

              <div className="viewer-hint">
                🖱️ Drag to rotate • Scroll to zoom • Right-click to pan
              </div>
            </div>

            {/* Info Panel */}
            <ModelInfo
              model={result.best_model}
              allCandidates={result.all_candidates}
              onSelectCandidate={setSelectedModelUrl}
              selectedUrl={selectedModelUrl}
            />
          </div>
        )}

        {/* Default Empty State */}
        {appState === 'idle' && (
          <div className="empty-state">
            <div className="empty-icon">🔮</div>
            <div className="empty-title">Ready to Explore</div>
            <div className="empty-description">
              Search for any concept above to activate the AI 3D visualization pipeline.
              The system will retrieve, validate, and render the best available 3D model
              — with intelligent fallback generation when needed.
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
