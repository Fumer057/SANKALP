'use client';

import { Suspense, useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, useGLTF, Environment, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';

interface ModelViewerProps {
  modelUrl: string;
  autoRotate?: boolean;
}

// Separate component for the actual 3D model to handle useGLTF hooks safely
function Model({ url }: { url: string }) {
  // Pre-check for valid GLB extension or common URL patterns
  const isValidUrl = url && (url.includes('.glb') || url.includes('.gltf') || url.includes('static/generated'));
  
  const { scene } = useGLTF(isValidUrl ? url : '/static/models/box.glb');
  const ref = useRef<THREE.Group>(null);

  return (
    <group ref={ref}>
      <primitive 
        object={scene} 
        scale={2} 
        position={[0, -0.5, 0]} 
        dispose={null} // Prevent unmount crashes
      />
    </group>
  );
}

function LoadingFallback() {
  return (
    <mesh>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#6C63FF" wireframe />
    </mesh>
  );
}

// Error Boundary for the Canvas specifically
class CanvasErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean }> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() { return { hasError: true }; }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center h-full w-full bg-black/20 text-white/40 text-sm italic">
          3D Engine Error: Model format incompatible or unreachable.
        </div>
      );
    }
    return this.props.children;
  }
}

import React from 'react';

export default function ModelViewer({ modelUrl, autoRotate = true }: ModelViewerProps) {
  const [loadError, setLoadError] = useState(false);
  const isSketchfab = modelUrl.includes('sketchfab.com');
  const isEmpty = !modelUrl || modelUrl === '';

  if (isEmpty) {
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
    <div className="viewer-canvas">
      <CanvasErrorBoundary>
        <Canvas
          camera={{ position: [3, 2, 5], fov: 45 }}
          gl={{ antialias: true, alpha: true, logarithmicDepthBuffer: true }}
          style={{ background: 'transparent' }}
          onError={() => setLoadError(true)}
        >
          <ambientLight intensity={0.8} />
          <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} />
          <pointLight position={[-10, -10, -10]} intensity={0.5} />
          <Environment preset="city" />
          
          <Suspense fallback={<LoadingFallback />}>
            {!loadError && <Model url={modelUrl} />}
          </Suspense>

          <ContactShadows position={[0, -1.5, 0]} opacity={0.3} scale={10} blur={2.5} />
          <OrbitControls 
            autoRotate={autoRotate} 
            autoRotateSpeed={1.0} 
            enablePan={true} 
            enableZoom={true} 
            minDistance={1} 
            maxDistance={20} 
          />
        </Canvas>
      </CanvasErrorBoundary>
    </div>
  );
}
