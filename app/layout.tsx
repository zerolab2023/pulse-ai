import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Pulse AI — 슬랙·노션을 읽는 스타트업 AI 비서',
  description: '매일 슬랙과 노션을 분석해서 병목을 찾고, 유니콘 성장을 가속화합니다. TOC·ONA·OKR 기반 학술적 분석.',
  openGraph: {
    title: 'Pulse AI — 스타트업 병목을 없애는 AI 비서',
    description: '슬랙·노션 연동 → 매일 병목 리포트 → 유니콘 가속',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="bg-gray-950 text-white antialiased">{children}</body>
    </html>
  );
}
