import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // @ts-ignore Ignore type error
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  // Ensure we don't accidentally try to optimize external 3D model thumbnails if we add them
  images: {
    unoptimized: true,
  }
};

export default nextConfig;
