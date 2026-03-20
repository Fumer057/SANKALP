'use client';

import { useState, FormEvent, useEffect } from 'react';
import dynamic from 'next/dynamic';
import PipelineStatus from '@/components/PipelineStatus';
import ModelInfo from '@/components/ModelInfo';

// Dynamically import ModelViewer with SSR disabled
const ModelViewer = dynamic(() => import('@/components/ModelViewer'), {
  ssr: false,
  loading: () => (
    <div className="loading-container">
      <div className="loading-spinner" />
      <div className="loading-text">Initializing 3D Engine...</div>
    </div>
  ),
});

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://sankalp-backend.render.com';

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
    source: string;
    confidence_score: number;
    url: string;
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

  const handleSearch = async (searchQuery?: string, forceGenerate: boolean = false) => {
    const q = searchQuery || query;
    if (!q.trim()) return;

    setAppState('searching');
    setResult(null);
    setError('');
    setCurrentStage(1);

    try {
      const response = await fetch(`${BACKEND_URL}/api/search?q=${encodeURIComponent(q)}${forceGenerate ? '&force_generate=true' : ''}`, { 
        cache: 'no-store',
        headers: { 'Accept': 'application/json' }
      });
      
      if (!response.ok) throw new Error(`Backend Offline or Error: ${response.status}`);

      const data: SearchResult = await response.json();
      
      if (!data || data.status !== 'success') {
          throw new Error("Invalid response from AI Pipeline");
      }

      setResult(data);
      setSelectedModelUrl(data.best_model?.url || '');
      setCurrentStage(data.pipeline_stages.length);
      setAppState('results');
    } catch (err) {
      console.error("Search Error:", err);
      setError(err instanceof Error ? err.message : 'The AI Pipeline is currently over capacity. Please try again in a few moments.');
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
        <section className="search-section">
          <h1 className="search-title">
            Visualize Any Concept<br />in 3D
          </h1>
          <p className="search-subtitle">
            Strict Shap-E AI Generation active. Optimized for high-reliability 3D reconstruction.
          </p>
          <form onSubmit={handleSubmit} className="search-bar-wrapper">
            <input
              id="search-input"
              className="search-bar"
              type="text"
              placeholder='Try "Human Heart", "Solar System"...'
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={appState === 'searching'}
            />
            <button
              id="search-button"
              className="search-btn"
              type="submit"
              disabled={appState === 'searching' || !query.trim()}
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

        {(appState === 'searching' || appState === 'results') && result?.pipeline_stages && (
          <PipelineStatus stages={result.pipeline_stages} currentStage={currentStage} />
        )}

        {appState === 'searching' && (
          <div className="loading-container animate-fade-in-up">
            <div className="loading-spinner" />
            <div className="loading-text">Activating Shap-E AI Engine...</div>
            <div className="loading-subtext">
              Synthesizing 3D geometry from semantic prompt. This normally takes 15-30 seconds.
            </div>
          </div>
        )}

        {appState === 'error' && (
          <div className="empty-state animate-fade-in-up">
            <div className="empty-icon">⚠️</div>
            <div className="empty-title">Pipeline Unavailable</div>
            <div className="empty-description">
              {error}
              <br /><br />
              <button 
                onClick={() => setAppState('idle')}
                className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm transition-all"
              >
                Return to Search
              </button>
            </div>
          </div>
        )}

        {appState === 'results' && result?.best_model && (
          <div className="results-section animate-fade-in-up">
            <div className="viewer-container">
              <div className="viewer-overlay-top">
                <span className={`viewer-badge ${result.is_fallback ? 'fallback' : 'success'}`}>
                  {result.is_fallback ? '🤖 AI Generated (Shap-E)' : '✓ Verified Asset'}
                </span>
              </div>

              <ModelViewer modelUrl={selectedModelUrl} autoRotate={true} />

              <div className="viewer-hint">
                🖱️ Drag to rotate • Scroll to zoom
              </div>
            </div>

            <div className="flex flex-col gap-4 w-full max-w-sm">
              <ModelInfo
                model={result.best_model}
                allCandidates={result.all_candidates}
                onSelectCandidate={setSelectedModelUrl}
                selectedUrl={selectedModelUrl}
              />
              
              {!result.is_fallback && (
                <div className="info-card animate-fade-in-up mt-2 p-4 text-center bg-white/5 border border-white/10 rounded-xl">
                  <p className="text-sm text-gray-400 mb-3">
                    Need higher fidelity? Trigger custom Shap-E generation.
                  </p>
                  <button
                    onClick={() => handleSearch(query, true)}
                    className="w-full py-3 px-4 bg-gradient-to-r from-[#6C63FF] to-[#8A7FFF] hover:from-[#5A52D5] hover:to-[#786DE6] text-white rounded-lg font-medium transition-all shadow-[0_0_15px_rgba(108,99,255,0.3)]"
                  >
                    ✨ Force Shap-E Generation
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {appState === 'idle' && (
          <div className="empty-state">
            <div className="empty-icon">🔮</div>
            <div className="empty-title">AI Engine Ready</div>
            <div className="empty-description">
              SANKALP is now strictly locked to the stable Shap-E core. 
              Search any concept to start the high-fidelity visualization pipeline.
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
