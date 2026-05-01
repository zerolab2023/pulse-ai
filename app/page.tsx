'use client';

import { useState } from 'react';

const FRAMEWORKS = [
  { name: 'TOC', full: '제약 이론', desc: '시스템 병목 식별' },
  { name: 'ONA', full: '조직 네트워크 분석', desc: '사일로·소통 단절 탐지' },
  { name: 'OKR', full: 'OKR 정렬도', desc: '목표와 실제 업무 격차 측정' },
  { name: 'DORA', full: 'DORA Metrics', desc: '개발팀 속도·안정성 지표' },
  { name: 'PSI', full: '심리적 안전감', desc: '팀 건강도·의사소통 패턴' },
];

const HOW = [
  { step: '01', title: '슬랙·노션 연동', desc: '5분 설치. Slack workspace와 Notion workspace를 연결하면 끝.', icon: '🔌' },
  { step: '02', title: 'AI가 매일 분석', desc: 'TOC·ONA·OKR 프레임워크 기반으로 병목, 사일로, OKR 이탈을 자동 감지.', icon: '🧠' },
  { step: '03', title: '매일 아침 리포트', desc: '슬랙 또는 이메일로 "오늘 당신 회사 상태 + 해결해야 할 것 TOP 3"를 전달.', icon: '📬' },
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
    <main style={{ fontFamily: "'Noto Sans KR', -apple-system, sans-serif" }}>

      {/* Nav — light */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 32px', height: 56,
        background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(8px)',
        borderBottom: '1px solid #f0f0f0',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 28, height: 28, borderRadius: 8, background: '#111', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: 'white', fontSize: 12, fontWeight: 700 }}>P</span>
          </div>
          <span style={{ fontWeight: 700, fontSize: 15, color: '#111' }}>Pulse AI</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <a href="mailto:hello@pulse-ai.kr" style={{ fontSize: 13, color: '#555', textDecoration: 'none' }}>
            이메일 문의 ↗
          </a>
          <a href="#waitlist" style={{
            fontSize: 13, fontWeight: 600, color: 'white',
            background: '#111', padding: '8px 18px', borderRadius: 8,
            textDecoration: 'none',
          }}>
            사전 예약하기
          </a>
        </div>
      </nav>

      {/* Hero — white */}
      <section style={{ paddingTop: 140, paddingBottom: 80, textAlign: 'center', background: 'white' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: '#f5f5f5', border: '1px solid #e5e5e5', borderRadius: 999, padding: '5px 14px', fontSize: 12, color: '#555', marginBottom: 32 }}>
          <span style={{ width: 7, height: 7, background: '#22c55e', borderRadius: '50%', display: 'inline-block' }} />
          사전 예약 {count}명 · 베타 출시 준비 중
        </div>

        <h1 style={{ fontSize: 52, fontWeight: 800, color: '#0a0a0a', lineHeight: 1.15, marginBottom: 12, letterSpacing: '-0.02em' }}>
          스타트업 성장을 막는<br />병목, AI가 찾아드립니다
        </h1>

        {/* Integration logos */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, margin: '20px 0 28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#f9f5ff', border: '1px solid #e9d5ff', borderRadius: 999, padding: '6px 14px' }}>
            <span style={{ fontSize: 16 }}>💬</span>
            <span style={{ fontSize: 13, fontWeight: 600, color: '#7c3aed' }}>Slack</span>
          </div>
          <span style={{ color: '#ccc', fontSize: 18 }}>+</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#fff7ed', border: '1px solid #fed7aa', borderRadius: 999, padding: '6px 14px' }}>
            <span style={{ fontSize: 16 }}>📝</span>
            <span style={{ fontSize: 13, fontWeight: 600, color: '#c2410c' }}>Notion</span>
          </div>
          <span style={{ color: '#ccc', fontSize: 18 }}>→</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 999, padding: '6px 14px' }}>
            <span style={{ fontSize: 16 }}>📊</span>
            <span style={{ fontSize: 13, fontWeight: 600, color: '#15803d' }}>Daily Report</span>
          </div>
        </div>

        <p style={{ fontSize: 17, color: '#666', maxWidth: 520, margin: '0 auto 36px', lineHeight: 1.75 }}>
          매일 아침, AI가 팀의 대화와 문서를 분석해서<br />
          TOC·ONA·OKR 기반으로 병목을 짚어드립니다.
        </p>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
          <a href="#waitlist" style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            background: '#111', color: 'white', fontSize: 15, fontWeight: 600,
            padding: '14px 28px', borderRadius: 10, textDecoration: 'none',
          }}>
            무료 사전 예약하기 →
          </a>
          <a href="#how" style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            background: 'white', color: '#333', fontSize: 15, fontWeight: 500,
            padding: '14px 24px', borderRadius: 10, textDecoration: 'none',
            border: '1px solid #e5e5e5',
          }}>
            어떻게 작동하나요?
          </a>
        </div>
        <p style={{ fontSize: 12, color: '#aaa', marginTop: 14 }}>베타 출시 알림 + 얼리버드 50% 할인</p>
      </section>

      {/* Dashboard mockup — dark */}
      <section style={{ background: '#0a0a0a', padding: '64px 24px' }}>
        <div style={{ maxWidth: 860, margin: '0 auto' }}>
          {/* Mac window chrome */}
          <div style={{ background: '#1a1a1a', borderRadius: '14px 14px 0 0', padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 8, borderBottom: '1px solid #2a2a2a' }}>
            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#ef4444' }} />
            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#f59e0b' }} />
            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#22c55e' }} />
            <span style={{ color: '#555', fontSize: 12, marginLeft: 8, fontFamily: 'monospace' }}>Pulse Daily Report — 2026.05.02</span>
          </div>
          {/* Report content */}
          <div style={{ background: '#111', borderRadius: '0 0 14px 14px', padding: 28, border: '1px solid #222', borderTop: 'none' }}>
            {/* Score row */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 }}>
              <div>
                <div style={{ fontSize: 11, color: '#555', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 6 }}>조직 건강도</div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
                  <span style={{ fontSize: 48, fontWeight: 800, color: 'white' }}>64</span>
                  <span style={{ fontSize: 20, color: '#555' }}>/100</span>
                  <span style={{ fontSize: 13, color: '#ef4444', background: 'rgba(239,68,68,0.1)', padding: '3px 8px', borderRadius: 6 }}>▼ 8</span>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 12 }}>
                {[
                  { label: 'TOC', val: '2', unit: '병목', color: '#ef4444' },
                  { label: 'OKR', val: '14%', unit: '얼라인', color: '#f59e0b' },
                  { label: 'DORA', val: 'Top 25%', unit: '', color: '#22c55e' },
                ].map(m => (
                  <div key={m.label} style={{ background: '#1a1a1a', border: '1px solid #2a2a2a', borderRadius: 10, padding: '10px 16px', textAlign: 'center', minWidth: 80 }}>
                    <div style={{ fontSize: 10, color: '#555', fontWeight: 600, letterSpacing: '0.06em', marginBottom: 4 }}>{m.label}</div>
                    <div style={{ fontSize: 18, fontWeight: 700, color: m.color }}>{m.val}</div>
                    {m.unit && <div style={{ fontSize: 10, color: '#555', marginTop: 2 }}>{m.unit}</div>}
                  </div>
                ))}
              </div>
            </div>
            {/* Issues */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                { priority: '긴급', color: '#ef4444', bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.2)', title: '디자인→개발 핸드오프 병목 (TOC)', desc: '평균 대기 2.3일 · 권고: #design-review 응답 SLA 설정' },
                { priority: '주의', color: '#f59e0b', bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.2)', title: 'Q2 OKR 이탈 감지 (OKR)', desc: '이번 주 슬랙 대화 중 Q2 OKR 관련 14% · 권고: 월요일 올핸즈 재정렬' },
                { priority: '양호', color: '#22c55e', bg: 'rgba(34,197,94,0.08)', border: 'rgba(34,197,94,0.2)', title: '개발팀 DORA 지표 상위 25% (DORA)', desc: '배포 빈도 · 리드타임 모두 업계 상위권' },
              ].map(item => (
                <div key={item.title} style={{ display: 'flex', alignItems: 'flex-start', gap: 12, background: item.bg, border: `1px solid ${item.border}`, borderRadius: 10, padding: '12px 16px' }}>
                  <span style={{ fontSize: 11, fontWeight: 700, color: item.color, background: `rgba(0,0,0,0.3)`, padding: '2px 8px', borderRadius: 4, flexShrink: 0, marginTop: 1 }}>{item.priority}</span>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'white', marginBottom: 3 }}>{item.title}</div>
                    <div style={{ fontSize: 12, color: '#888' }}>{item.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* How it works — white */}
      <section id="how" style={{ background: 'white', padding: '80px 24px' }}>
        <div style={{ maxWidth: 860, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 52 }}>
            <h2 style={{ fontSize: 32, fontWeight: 800, color: '#0a0a0a', marginBottom: 10 }}>어떻게 작동하나요?</h2>
            <p style={{ fontSize: 15, color: '#888' }}>3단계로 끝납니다</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
            {HOW.map(h => (
              <div key={h.step} style={{ border: '1px solid #f0f0f0', borderRadius: 14, padding: 24 }}>
                <div style={{ fontSize: 28, marginBottom: 14 }}>{h.icon}</div>
                <div style={{ fontSize: 11, fontWeight: 700, color: '#aaa', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 6 }}>STEP {h.step}</div>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: '#111', marginBottom: 8 }}>{h.title}</h3>
                <p style={{ fontSize: 13, color: '#888', lineHeight: 1.65 }}>{h.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Frameworks — light gray */}
      <section style={{ background: '#f9f9f9', padding: '80px 24px' }}>
        <div style={{ maxWidth: 860, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <h2 style={{ fontSize: 32, fontWeight: 800, color: '#0a0a0a', marginBottom: 10 }}>학술 프레임워크 기반</h2>
            <p style={{ fontSize: 15, color: '#888', maxWidth: 440, margin: '0 auto' }}>감이 아닌 데이터. 세계적으로 검증된 조직 이론으로 분석합니다.</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 10 }}>
            {FRAMEWORKS.map(f => (
              <div key={f.name} style={{ background: 'white', border: '1px solid #ebebeb', borderRadius: 12, padding: '16px 12px', textAlign: 'center' }}>
                <div style={{ fontSize: 17, fontWeight: 800, color: '#111', marginBottom: 4 }}>{f.name}</div>
                <div style={{ fontSize: 11, fontWeight: 600, color: '#333', marginBottom: 4 }}>{f.full}</div>
                <div style={{ fontSize: 11, color: '#aaa' }}>{f.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Waitlist — white */}
      <section id="waitlist" style={{ background: 'white', padding: '100px 24px' }}>
        <div style={{ maxWidth: 440, margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ fontSize: 34, fontWeight: 800, color: '#0a0a0a', marginBottom: 10 }}>베타 출시 알림 받기</h2>
          <p style={{ fontSize: 14, color: '#888', marginBottom: 4 }}>사전 예약자에게만 얼리버드 50% 할인 제공</p>
          <p style={{ fontSize: 13, fontWeight: 600, color: '#6366f1', marginBottom: 36 }}>현재 {count}명 예약 완료</p>

          {done ? (
            <div style={{ background: '#f9f5ff', border: '1px solid #e9d5ff', borderRadius: 14, padding: 36, textAlign: 'center' }}>
              <div style={{ fontSize: 40, marginBottom: 12 }}>🎉</div>
              <h3 style={{ fontSize: 18, fontWeight: 700, color: '#111', marginBottom: 6 }}>예약 완료!</h3>
              <p style={{ fontSize: 14, color: '#888' }}>베타 오픈 시 가장 먼저 알려드릴게요.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <input
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="이메일 주소"
                style={{ width: '100%', background: 'white', border: '1px solid #e5e5e5', borderRadius: 10, padding: '14px 16px', fontSize: 14, color: '#111', outline: 'none', boxSizing: 'border-box' }}
              />
              <input
                type="text"
                value={company}
                onChange={e => setCompany(e.target.value)}
                placeholder="회사명 (선택)"
                style={{ width: '100%', background: 'white', border: '1px solid #e5e5e5', borderRadius: 10, padding: '14px 16px', fontSize: 14, color: '#111', outline: 'none', boxSizing: 'border-box' }}
              />
              <select
                value={role}
                onChange={e => setRole(e.target.value)}
                style={{ width: '100%', background: 'white', border: '1px solid #e5e5e5', borderRadius: 10, padding: '14px 16px', fontSize: 14, color: role ? '#111' : '#aaa', outline: 'none', boxSizing: 'border-box' }}
              >
                <option value="">직책 선택 (선택)</option>
                <option value="ceo">대표 / CEO</option>
                <option value="cto">CTO / 개발 리드</option>
                <option value="coo">COO / 운영</option>
                <option value="pm">PM / PO</option>
                <option value="other">기타</option>
              </select>
              {error && <p style={{ color: '#ef4444', fontSize: 13 }}>{error}</p>}
              <button
                type="submit"
                disabled={loading}
                style={{ width: '100%', background: loading ? '#ccc' : '#111', color: 'white', fontWeight: 700, padding: '15px', borderRadius: 10, fontSize: 15, border: 'none', cursor: loading ? 'default' : 'pointer', marginTop: 4 }}
              >
                {loading ? '처리 중...' : '무료 사전 예약하기 →'}
              </button>
              <p style={{ fontSize: 12, color: '#bbb' }}>스팸 없음. 베타 오픈 시 1회 알림 이메일만 발송.</p>
            </form>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid #f0f0f0', padding: '32px 24px', textAlign: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, marginBottom: 8 }}>
          <div style={{ width: 20, height: 20, borderRadius: 6, background: '#111', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: 'white', fontSize: 10, fontWeight: 700 }}>P</span>
          </div>
          <span style={{ fontSize: 14, fontWeight: 600, color: '#333' }}>Pulse AI</span>
        </div>
        <p style={{ fontSize: 13, color: '#bbb' }}>
          © 2026 Pulse AI · <a href="mailto:hello@pulse-ai.kr" style={{ color: '#999', textDecoration: 'none' }}>hello@pulse-ai.kr</a>
        </p>
      </footer>

    </main>
  );
}
