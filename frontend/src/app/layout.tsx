import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "SANKALP — AI 3D Visualization System",
  description:
    "An intelligent system that retrieves, validates, and presents 3D visual representations of any concept using AI-powered pipelines with fallback generation.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <header className="app-header">
          <div className="header-inner">
            <Link href="/" className="logo hover:opacity-80 transition-opacity" style={{ textDecoration: 'none' }}>
              <div className="logo-icon">S</div>
              <div>
                <div className="logo-text">SANKALP</div>
                <div className="logo-tag">AI 3D Visualization</div>
              </div>
            </Link>
            
            <nav className="flex items-center gap-8" style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
              <Link href="/" style={{ color: 'var(--color-text-secondary)', textDecoration: 'none', fontSize: '14px', fontWeight: 500 }} className="hover:text-white transition-colors">
                Search
              </Link>
              <Link href="/gallery" style={{ color: 'var(--color-text-secondary)', textDecoration: 'none', fontSize: '14px', fontWeight: 500 }} className="hover:text-white transition-colors">
                Model Gallery
              </Link>
              <div className="header-badge">⚡ Prototype v0.1</div>
            </nav>
          </div>
        </header>

        {children}
      </body>
    </html>
  );
}
