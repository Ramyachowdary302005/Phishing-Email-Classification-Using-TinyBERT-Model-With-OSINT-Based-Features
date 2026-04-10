import React, { useState } from 'react';
import { ShieldCheck, Mail, Lock, Eye, EyeOff, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter your email and password.');
      return;
    }
    setLoading(true);
    setError('');
    const ok = await login(email, password);
    setLoading(false);
    if (!ok) setError('Invalid email or password. Try demo@phishguard.ai / demo123');
  };

  const fillDemo = () => {
    setEmail('demo@phishguard.ai');
    setPassword('demo123');
    setError('');
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0f1e 0%, #0d1b2a 40%, #0a1628 70%, #061020 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem',
      fontFamily: "'Inter', 'Segoe UI', sans-serif",
      position: 'relative',
      overflow: 'hidden',
    }}>

      {/* Animated background orbs */}
      <div style={{
        position: 'absolute', top: '10%', left: '15%', width: '320px', height: '320px',
        background: 'radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%)',
        borderRadius: '50%', filter: 'blur(40px)', animation: 'float1 8s ease-in-out infinite',
      }} />
      <div style={{
        position: 'absolute', bottom: '15%', right: '12%', width: '280px', height: '280px',
        background: 'radial-gradient(circle, rgba(139,92,246,0.10) 0%, transparent 70%)',
        borderRadius: '50%', filter: 'blur(40px)', animation: 'float2 10s ease-in-out infinite',
      }} />
      <div style={{
        position: 'absolute', top: '55%', left: '5%', width: '200px', height: '200px',
        background: 'radial-gradient(circle, rgba(16,185,129,0.08) 0%, transparent 70%)',
        borderRadius: '50%', filter: 'blur(30px)',
      }} />

      {/* Grid overlay */}
      <div style={{
        position: 'absolute', inset: 0,
        backgroundImage: 'linear-gradient(rgba(59,130,246,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(59,130,246,0.04) 1px, transparent 1px)',
        backgroundSize: '50px 50px',
        mask: 'radial-gradient(ellipse at center, black 30%, transparent 80%)',
      }} />

      {/* Card */}
      <div style={{
        position: 'relative', zIndex: 10,
        width: '100%', maxWidth: '420px',
        background: 'rgba(15, 23, 42, 0.85)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(59,130,246,0.2)',
        borderRadius: '20px',
        padding: '2.5rem',
        boxShadow: '0 25px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(59,130,246,0.05) inset',
      }}>

        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            width: '70px', height: '70px', borderRadius: '18px',
            background: 'linear-gradient(135deg, #1d4ed8, #7c3aed)',
            boxShadow: '0 0 30px rgba(99,102,241,0.4)',
            marginBottom: '1rem',
          }}>
            <ShieldCheck size={36} color="white" />
          </div>
          <h1 style={{
            fontSize: '1.75rem', fontWeight: 800, margin: 0,
            background: 'linear-gradient(135deg, #60a5fa, #a78bfa)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            letterSpacing: '-0.02em',
          }}>PhishGuard AI</h1>
          <p style={{ color: '#64748b', fontSize: '0.875rem', margin: '0.35rem 0 0' }}>
            Threat Intelligence Platform
          </p>
        </div>

        {/* Welcome text */}
        <div style={{ marginBottom: '1.75rem' }}>
          <h2 style={{ color: '#e2e8f0', fontSize: '1.125rem', fontWeight: 600, margin: '0 0 0.25rem' }}>
            Welcome back
          </h2>
          <p style={{ color: '#475569', fontSize: '0.8rem', margin: 0 }}>
            Sign in to your security dashboard
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>

          {/* Email */}
          <div>
            <label style={{ display: 'block', color: '#94a3b8', fontSize: '0.8rem', fontWeight: 500, marginBottom: '0.4rem' }}>
              Email Address
            </label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} color="#475569" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@phishguard.ai"
                style={{
                  width: '100%', boxSizing: 'border-box',
                  background: 'rgba(30,41,59,0.8)',
                  border: `1px solid ${error ? 'rgba(239,68,68,0.5)' : 'rgba(71,85,105,0.5)'}`,
                  borderRadius: '10px', padding: '0.7rem 0.75rem 0.7rem 2.5rem',
                  color: '#e2e8f0', fontSize: '0.875rem', outline: 'none',
                  transition: 'border-color 0.2s',
                }}
                onFocus={e => e.target.style.borderColor = 'rgba(96,165,250,0.6)'}
                onBlur={e => e.target.style.borderColor = error ? 'rgba(239,68,68,0.5)' : 'rgba(71,85,105,0.5)'}
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label style={{ display: 'block', color: '#94a3b8', fontSize: '0.8rem', fontWeight: 500, marginBottom: '0.4rem' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={16} color="#475569" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                style={{
                  width: '100%', boxSizing: 'border-box',
                  background: 'rgba(30,41,59,0.8)',
                  border: `1px solid ${error ? 'rgba(239,68,68,0.5)' : 'rgba(71,85,105,0.5)'}`,
                  borderRadius: '10px', padding: '0.7rem 2.5rem 0.7rem 2.5rem',
                  color: '#e2e8f0', fontSize: '0.875rem', outline: 'none',
                  transition: 'border-color 0.2s',
                }}
                onFocus={e => e.target.style.borderColor = 'rgba(96,165,250,0.6)'}
                onBlur={e => e.target.style.borderColor = error ? 'rgba(239,68,68,0.5)' : 'rgba(71,85,105,0.5)'}
              />
              <button
                type="button"
                onClick={() => setShowPassword(p => !p)}
                style={{
                  position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)',
                  background: 'none', border: 'none', cursor: 'pointer', padding: 0,
                  color: '#475569',
                }}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* Error message */}
          {error && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem',
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
              borderRadius: '8px', padding: '0.6rem 0.75rem',
              color: '#f87171', fontSize: '0.8rem',
            }}>
              <AlertCircle size={14} style={{ flexShrink: 0 }} />
              {error}
            </div>
          )}

          {/* Login button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              marginTop: '0.25rem',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem',
              background: loading ? 'rgba(37,99,235,0.5)' : 'linear-gradient(135deg, #2563eb, #7c3aed)',
              color: 'white', border: 'none', borderRadius: '10px',
              padding: '0.8rem', fontSize: '0.9rem', fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer',
              boxShadow: loading ? 'none' : '0 4px 20px rgba(99,102,241,0.35)',
              transition: 'all 0.2s',
            }}
          >
            {loading ? (
              <>
                <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
                Authenticating...
              </>
            ) : (
              'Sign In to Dashboard'
            )}
          </button>
        </form>

        {/* Demo credentials hint */}
        <div style={{
          marginTop: '1.5rem',
          background: 'rgba(30,41,59,0.6)',
          border: '1px solid rgba(71,85,105,0.4)',
          borderRadius: '10px', padding: '0.75rem 1rem',
        }}>
          <p style={{ color: '#64748b', fontSize: '0.75rem', margin: '0 0 0.5rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Demo Credentials
          </p>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ color: '#94a3b8', fontSize: '0.78rem', margin: '0.1rem 0' }}>
                <span style={{ color: '#60a5fa' }}>Email:</span> demo@phishguard.ai
              </p>
              <p style={{ color: '#94a3b8', fontSize: '0.78rem', margin: '0.1rem 0' }}>
                <span style={{ color: '#60a5fa' }}>Password:</span> demo123
              </p>
            </div>
            <button
              onClick={fillDemo}
              style={{
                background: 'rgba(37,99,235,0.2)', border: '1px solid rgba(37,99,235,0.4)',
                color: '#60a5fa', borderRadius: '8px', padding: '0.35rem 0.75rem',
                fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer',
              }}
            >
              Fill
            </button>
          </div>
        </div>

        <p style={{ textAlign: 'center', color: '#334155', fontSize: '0.75rem', marginTop: '1.5rem', marginBottom: 0 }}>
          © 2026 PhishGuard AI • Cybersecurity Intelligence
        </p>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        @keyframes float1 { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-20px)} }
        @keyframes float2 { 0%,100%{transform:translateY(0)} 50%{transform:translateY(20px)} }
        @keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
      `}</style>
    </div>
  );
}
