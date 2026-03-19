'use client';

import { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, useGLTF, Environment, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';

interface ModelViewerProps {
  modelUrl: string;
  autoRotate?: boolean;
}

function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url);
  const ref = useRef<THREE.Group>(null);


  return (
    <group ref={ref}>
      <primitive object={scene} scale={2} position={[0, -1, 0]} />
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

export default function ModelViewer({ modelUrl, autoRotate = true }: ModelViewerProps) {
  const isSketchfab = modelUrl.includes('sketchfab.com');

  if (isSketchfab) {
    return (
      <div className="viewer-canvas relative overflow-hidden rounded-xl border border-white/10">
        <iframe
          title="Sketchfab Viewer"
          src={`${modelUrl}?autostart=1&internal=1&tracking=0&ui_ar=0&ui_infos=0&ui_snapshots=1&ui_stop=0&ui_theatre=1&ui_watermark=0`}
          className="h-full w-full border-0"
          allow="autoplay; fullscreen; xr-spatial-tracking"
          execution-while-out-of-viewport
          execution-while-not-rendered
          web-share
        ></iframe>
      </div>
    );
  }

  return (
    <div className="viewer-canvas">
      <Canvas
        camera={{ position: [3, 2, 5], fov: 45 }}
        gl={{ antialias: true, alpha: true }}
        style={{ background: 'transparent' }}
      >
        {/* Basic Fixed Lighting */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 10, 5]} intensity={1} />
        <pointLight position={[-5, 5, -5]} intensity={0.5} />

        {/* Environment */}
        <Environment preset="city" />

        {/* Model */}
        <Suspense fallback={<LoadingFallback />}>
          <Model url={modelUrl} />
        </Suspense>

        {/* Shadows */}
        <ContactShadows
          position={[0, -1.5, 0]}
          opacity={0.3}
          scale={10}
          blur={2.5}
        />

        {/* Controls */}
        <OrbitControls
          autoRotate={autoRotate}
          autoRotateSpeed={1.0}
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={1.5}
          maxDistance={15}
        />
      </Canvas>
    </div>
  );
}
