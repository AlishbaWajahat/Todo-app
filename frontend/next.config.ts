import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8001',
        pathname: '/uploads/**',
      },
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  reactStrictMode: true,
  // Force rebuild to pick up environment variables
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; connect-src 'self' http://localhost:* https://alishba20-05-todp-app.hf.space https://cdn.platform.openai.com ws://localhost:*; img-src 'self' blob: data: https:; script-src 'self' 'unsafe-eval' 'unsafe-inline' https://cdn.platform.openai.com; style-src 'self' 'unsafe-inline'; frame-src 'self' https://cdn.platform.openai.com;",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
