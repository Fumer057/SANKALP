'use client';

import { useEffect, useState } from 'react';

interface ModelViewerProps {
  modelUrl: string;
  autoRotate?: boolean;
}

/**
 * Robust 3D Viewer using Google's <model-viewer> web component.
 * This is the industry standard for reliable 3D rendering on the web.
 */
export default function ModelViewer({ modelUrl, autoRotate = true }: ModelViewerProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const isSketchfab = modelUrl.includes('sketchfab.com');

  // Load the web component scripts dynamically
  useEffect(() => {
    const script = document.createElement('script');
    script.type = 'module';
    script.src = 'https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js';
    document.head.appendChild(script);
    
    return () => {
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, []);

  if (!modelUrl) {
    return (
      <div className="viewer-canvas flex items-center justify-center bg-black/20 text-white/20 italic">
        Select a model to initialize viewer...
      </div>
    );
  }

  if (isSketchfab) {
    return (
      <div className="viewer-canvas relative overflow-hidden rounded-xl border border-white/10">
        <iframe
          title="Sketchfab Viewer"
          src={`${modelUrl}?autostart=1&internal=1&tracking=0&ui_ar=0&ui_infos=0&ui_snapshots=1&ui_stop=0&ui_theatre=1&ui_watermark=0`}
          className="h-full w-full border-0"
          allow="autoplay; fullscreen; xr-spatial-tracking"
        ></iframe>
      </div>
    );
  }

  return (
    <div className="viewer-canvas flex flex-col items-center justify-center relative overflow-hidden bg-white/5 rounded-xl border border-white/10">
      {/* Type-safe model-viewer usage with custom-elements support */}
      {/* @ts-ignore */}
      <model-viewer
        src={modelUrl}
        alt="AI Generated 3D Model"
        auto-rotate={autoRotate ? "true" : "false"}
        camera-controls
        shadow-intensity="1"
        environment-image="neutral"
        exposure="1"
        loading="eager"
        style={{ width: '100%', height: '100%', outline: 'none' }}
        onLoad={() => setIsLoaded(true)}
      >
        {!isLoaded && (
          <div slot="poster" className="flex items-center justify-center h-full w-full bg-black/10">
            <div className="loading-spinner" />
          </div>
        )}
        
        {/* Progress Bar Slot */}
        <div slot="progress-bar" style={{ display: 'none' }} />
        
        {/* Error Fallback */}
        <div className="model-viewer-error absolute inset-0 flex items-center justify-center pointer-events-none opacity-0 transition-opacity duration-300">
           Failed to render asset.
        </div>
        {/* @ts-ignore */}
      </model-viewer>
    </div>
  );
}
