'use client';

import { useState } from 'react';

const FRAMEWORKS = [
  { name: 'TOC', full: '제약 이론', desc: '시스템 병목 식별' },
  { name: 'ONA', full: '조직 네트워크 분석', desc: '사일로·소통 단절 탐지' },
  { name: 'OKR', full: 'OKR 정렬도', desc: '목표와 실제 업무 격차 측정' },
  { name: 'DORA', full: 'DORA Metrics', desc: '개발팀 속도·안정성 지표' },
  { name: 'PSI', full: '심리적 안전감', desc: '팀 건강도·의사소통 패턴' },
];

const PAINS = [
  { icon: '😓', text: '슬랙 채널 100개, 읽을 시간이 없다' },
  { icon: '🔍', text: '어디서 왜 막히는지 보이지 않는다' },
  { icon: '📊', text: '주간 보고는 있는데 진짜 병목은 모른다' },
  { icon: '🚀', text: '열심히 하는데 성장 속도가 나오지 않는다' },
];

const HOW = [
  {
    step: '01',
    title: '슬랙·노션 연동',
    desc: '5분 설치. Slack workspace와 Notion workspace를 연결하면 끝.',
    icon: '🔌',
  },
  {
    step: '02',
    title: 'AI가 매일 분석',
    desc: 'TOC·ONA·OKR 프레임워크 기반으로 병목, 사일로, OKR 이탈을 자동 감지.',
    icon: '🧠',
  },
  {
    step: '03',
    title: '매일 아침 리포트',
    desc: '슬랙 또는 이메일로 "오늘 당신 회사 상태 + 해결해야 할 것 TOP 3"를 전달.',
    icon: '📬',
  },
];

export default function Home() {
  const [email, setEmail] = useState('');
  const [company, setCompany] = useState('');
  const [role, setRole] = useState('');
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');
  const [count, setCount] = useState(47);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await fetch('/api/waitlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, company, role }),
      });
      if (!res.ok) throw new Error('서버 오류');
      setDone(true);
      setCount(c => c + 1);
    } catch {
      setError('잠시 후 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen">

      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 bg-gray-950/80 backdrop-blur-md border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-indigo-500 flex items-center justify-center">
            <span className="text-white text-xs font-bold">P</span>
          </div>
          <span className="font-bold text-white">Pulse</span>
        </div>
        <a href="#waitlist" className="text-sm bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg transition font-medium">
          사전 예약
        </a>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-24 px-6 text-center max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 bg-indigo-950/60 border border-indigo-500/30 rounded-full px-4 py-1.5 text-sm text-indigo-300 mb-8">
          <span className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse" />
          사전 예약 {count}명 돌파
        </div>
        <h1 className="text-4xl md:text-6xl font-extrabold leading-tight mb-6">
          <span className="gradient-text">슬랙·노션을 읽는</span>
          <br />
          스타트업 AI 비서
        </h1>
        <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          매일 아침, AI가 팀의 대화와 문서를 분석해서<br />
          병목을 찾고 유니콘이 되는 길을 알려드립니다.
        </p>
        <a
          href="#waitlist"
          className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-lg font-semibold px-8 py-4 rounded-2xl transition-all hover:scale-105 shadow-lg shadow-indigo-500/20"
        >
          무료 사전 예약하기 →
        </a>
        <p className="text-sm text-gray-600 mt-4">베타 출시 알림 + 얼리버드 50% 할인</p>
      </section>

      {/* Pain */}
      <section className="py-20 px-6 max-w-4xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-bold text-center mb-12 text-gray-100">
          이런 상황, 공감되시나요?
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {PAINS.map((p, i) => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-2xl p-5 flex items-start gap-4 card-glow transition">
              <span className="text-2xl">{p.icon}</span>
              <p className="text-gray-300 font-medium">{p.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 px-6 max-w-4xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-bold text-center mb-4 text-gray-100">어떻게 작동하나요?</h2>
        <p className="text-center text-gray-500 mb-12">3단계로 끝납니다</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {HOW.map((h) => (
            <div key={h.step} className="bg-gray-900 border border-gray-800 rounded-2xl p-6 card-glow transition">
              <div className="text-3xl mb-4">{h.icon}</div>
              <div className="text-xs font-bold text-indigo-400 mb-2">STEP {h.step}</div>
              <h3 className="text-lg font-bold text-white mb-2">{h.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{h.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Frameworks */}
      <section className="py-20 px-6 max-w-4xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-bold text-center mb-4 text-gray-100">학술 프레임워크 기반</h2>
        <p className="text-center text-gray-500 mb-12 max-w-xl mx-auto">
          감이 아닌 데이터. 세계적으로 검증된 조직 이론으로 분석합니다.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {FRAMEWORKS.map((f) => (
            <div key={f.name} className="bg-gray-900 border border-gray-800 rounded-2xl p-4 text-center card-glow transition">
              <div className="text-indigo-400 font-extrabold text-lg mb-1">{f.name}</div>
              <div className="text-white text-xs font-semibold mb-1">{f.full}</div>
              <div className="text-gray-500 text-xs">{f.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Sample report */}
      <section className="py-20 px-6 max-w-3xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-bold text-center mb-12 text-gray-100">매일 아침 이런 리포트가 옵니다</h2>
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 font-mono text-sm">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-gray-500 ml-2">Pulse Daily Report — 2026.05.02</span>
          </div>
          <div className="space-y-3 text-gray-300">
            <p><span className="text-indigo-400">📊 조직 건강도:</span> <span className="text-yellow-400 font-bold">64 / 100</span> <span className="text-gray-500">(지난주 대비 -8)</span></p>
            <p className="text-gray-500">──────────────────────────────</p>
            <p><span className="text-red-400">🔴 병목 #1 (TOC):</span> 디자인팀 → 개발팀 핸드오프</p>
            <p className="text-gray-400 pl-4">· 평균 대기시간 2.3일 (기준: 0.5일)</p>
            <p className="text-gray-400 pl-4">· 권고: #design-review 채널 응답 SLA 설정</p>
            <p className="text-gray-500">──────────────────────────────</p>
            <p><span className="text-orange-400">🟡 병목 #2 (OKR):</span> Q2 핵심 목표 이탈</p>
            <p className="text-gray-400 pl-4">· 이번 주 슬랙 대화 중 Q2 OKR 관련 14%만</p>
            <p className="text-gray-400 pl-4">· 권고: 월요일 올핸즈에서 재정렬 필요</p>
            <p className="text-gray-500">──────────────────────────────</p>
            <p><span className="text-green-400">✅ 잘 되고 있는 것:</span> 개발팀 DORA 지표 상위 25%</p>
          </div>
        </div>
      </section>

      {/* Waitlist */}
      <section id="waitlist" className="py-24 px-6">
        <div className="max-w-lg mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-extrabold mb-4 text-white">
            베타 출시 알림 받기
          </h2>
          <p className="text-gray-400 mb-2">사전 예약자에게만 얼리버드 50% 할인 제공</p>
          <p className="text-indigo-400 text-sm font-semibold mb-10">현재 {count}명 예약 완료</p>

          {done ? (
            <div className="bg-indigo-950/50 border border-indigo-500/40 rounded-2xl p-8 text-center">
              <div className="text-4xl mb-4">🎉</div>
              <h3 className="text-xl font-bold text-white mb-2">예약 완료!</h3>
              <p className="text-gray-400 text-sm">베타 오픈 시 가장 먼저 알려드릴게요.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-3">
              <input
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="이메일 주소"
                className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3.5 text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition text-sm"
              />
              <input
                type="text"
                value={company}
                onChange={e => setCompany(e.target.value)}
                placeholder="회사명 (선택)"
                className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3.5 text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition text-sm"
              />
              <select
                value={role}
                onChange={e => setRole(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3.5 text-white focus:outline-none focus:border-indigo-500 transition text-sm"
              >
                <option value="">직책 선택 (선택)</option>
                <option value="ceo">대표 / CEO</option>
                <option value="cto">CTO / 개발 리드</option>
                <option value="coo">COO / 운영</option>
                <option value="pm">PM / PO</option>
                <option value="other">기타</option>
              </select>
              {error && <p className="text-red-400 text-sm">{error}</p>}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold py-4 rounded-xl transition-all hover:scale-[1.02] text-base"
              >
                {loading ? '처리 중...' : '무료 사전 예약하기 →'}
              </button>
              <p className="text-xs text-gray-600">스팸 없음. 베타 오픈 시 1회 알림 이메일만 발송.</p>
            </form>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 px-6 border-t border-gray-900 text-center text-gray-600 text-sm">
        <div className="flex items-center justify-center gap-2 mb-2">
          <div className="w-5 h-5 rounded bg-indigo-600 flex items-center justify-center">
            <span className="text-white text-xs font-bold">P</span>
          </div>
          <span className="text-gray-400 font-semibold">Pulse AI</span>
        </div>
        <p>© 2026 Pulse AI · <a href="mailto:hello@pulse-ai.kr" className="hover:text-gray-400 transition">hello@pulse-ai.kr</a></p>
      </footer>

    </main>
  );
}
