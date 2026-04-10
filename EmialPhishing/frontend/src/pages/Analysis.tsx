import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input, Textarea } from '../components/common/Input';
import { Badge } from '../components/common/Badge';
import { Progress } from '../components/common/Progress';
import { api } from '../services/api';
import { useHistory } from '../context/HistoryContext';
import { AnalysisResponse } from '../types';
import {
  ShieldCheck, ShieldAlert, AlertTriangle, Activity,
  Info, Globe, Mail, CheckCircle2, XCircle, ArrowRight
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, LabelList
} from 'recharts';

export function Analysis() {
  const [senderEmail, setSenderEmail] = useState('');
  const [emailBody, setEmailBody] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);

  const { addHistory } = useHistory();

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!senderEmail || !emailBody) {
      setError('Both Sender Email and Email Body are required.');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    const requestPayload = { email_text: emailBody, headers: { from: senderEmail } };
    try {
      const res = await api.analyzeEmail(requestPayload);
      setResult(res);
      addHistory({ request: requestPayload, response: res });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred during analysis.');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setSenderEmail(''); setEmailBody(''); setResult(null); setError(null);
  };

  const isPhishing = result?.final_decision === 'Phishing';

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Email Analysis Scanner</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Perform high-fidelity inspection on suspect emails using AI &amp; OSINT.
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6 items-start">
        {/* ── Input Form ─────────────────────────────────────────────────── */}
        <Card className="shadow-lg border-gray-200 dark:border-gray-800">
          <CardHeader>
            <CardTitle>Security Scan</CardTitle>
            <CardDescription>Enter the email attributes to begin the deep-dive analysis.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleAnalyze} className="space-y-5">
              <Input
                label="Sender Address"
                placeholder="e.g. security-alert@verified-domain.com"
                type="email"
                value={senderEmail}
                onChange={e => setSenderEmail(e.target.value)}
                required
              />
              <Textarea
                label="Email Source/Text"
                placeholder="Paste the raw text of the email here..."
                value={emailBody}
                onChange={e => setEmailBody(e.target.value)}
                rows={8}
                required
              />
              {error && (
                <div className="p-3 rounded-lg bg-red-50 text-red-600 border border-red-200 dark:bg-red-900/20 dark:border-red-900 text-sm animate-in shake">
                  {error}
                </div>
              )}
              <div className="flex gap-3 pt-2">
                <Button type="submit" isLoading={loading} className="w-full h-11 text-base">
                  {loading ? 'Analyzing...' : 'Run Analysis'}
                </Button>
                <Button type="button" variant="outline" onClick={resetForm} disabled={loading} className="h-11">
                  Reset
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* ── Results ────────────────────────────────────────────────────── */}
        <div className="space-y-6">
          {loading && (
            <Card className="flex flex-col items-center justify-center p-20 space-y-6 border-dashed animate-pulse">
              <div className="relative">
                <div className="w-16 h-16 border-4 border-primary-500/20 border-t-primary-500 rounded-full animate-spin"></div>
                <Activity className="w-6 h-6 text-primary-500 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
              </div>
              <div className="text-xl font-bold text-center">Threat Intelligence Engine Running...</div>
              <p className="text-sm text-gray-400 max-w-[200px] text-center">Comparing heuristics with AI patterns and domain reputation...</p>
            </Card>
          )}

          {!loading && !result && (
            <Card className="flex flex-col items-center justify-center p-20 border-dashed text-gray-400 bg-gray-50/50 dark:bg-gray-900/10">
              <ShieldCheck className="w-16 h-16 mb-6 opacity-20" />
              <p className="text-center font-medium">Ready for input.<br/><span className="text-xs font-normal opacity-60">System armed and ready to analyze threats.</span></p>
            </Card>
          )}

          {result && (
            <div className="space-y-6 animate-in fade-in zoom-in-95 duration-500">

              {/* ── Final Verdict ───────────────────────────────────────── */}
              <Card className={`overflow-hidden border-2 shadow-2xl ${isPhishing
                ? 'border-red-500/50 bg-red-50/10 dark:bg-red-950/20'
                : 'border-green-500/50 bg-green-50/10 dark:bg-green-950/20'}`}>
                <div className={`h-2 ${isPhishing ? 'bg-red-500' : 'bg-green-500'}`} />
                <CardHeader className="pb-4">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-xl font-black uppercase tracking-wider">Analysis Result</CardTitle>
                    <Badge className="px-3 py-1 text-xs" variant={isPhishing ? 'danger' : 'success'}>
                      THREAT {isPhishing ? 'DETECTED' : 'CLEAR'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-start space-x-5">
                    <div className={`p-4 rounded-2xl ${isPhishing ? 'bg-red-100 text-red-600 dark:bg-red-900/30' : 'bg-green-100 text-green-600 dark:bg-green-900/30'}`}>
                      {isPhishing
                        ? <AlertTriangle className="w-10 h-10" />
                        : <ShieldCheck className="w-10 h-10" />}
                    </div>
                    <div className="space-y-1 pt-1 flex-1">
                      <div className={`text-3xl font-black ${isPhishing ? 'text-red-500' : 'text-green-500'}`}>
                        {result.final_decision.toUpperCase()}
                      </div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-300 leading-relaxed italic border-l-2 border-primary-500 pl-3 py-1">
                        "{result.reason}"
                      </p>
                    </div>
                  </div>

                  <div className="space-y-2 pt-2 border-t border-gray-100 dark:border-gray-800">
                    <div className="flex justify-between items-end mb-1">
                      <span className="text-xs font-bold uppercase text-gray-500">Security Confidence Score</span>
                      <span className={`text-lg font-black ${isPhishing ? 'text-red-500' : 'text-green-500'}`}>
                        {(result.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress
                      value={result.confidence * 100}
                      className="h-3 rounded-full bg-gray-200 dark:bg-gray-800"
                      indicatorClassName={isPhishing ? 'bg-gradient-to-r from-red-600 to-red-400' : 'bg-gradient-to-r from-green-600 to-green-400'}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* ── Technical Evidence Breakdown (OSINT) ────────────────── */}
              <Card className="border-gray-200 dark:border-gray-800 shadow-xl">
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-base font-bold flex items-center gap-2">
                      <Globe className="w-4 h-4 text-primary-500" />
                      Technical Evidence & OSINT
                    </CardTitle>
                    {result.osint_analysis?.is_trusted && (
                      <Badge variant="success" className="bg-green-500/10 text-green-600 border-green-500/20 text-[10px] uppercase font-black">
                        ✓ Verified Authority
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  {result.osint_analysis ? (
                    <>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 bg-gray-50 dark:bg-gray-900/40 rounded-xl border border-gray-100 dark:border-gray-800 shadow-inner">
                          <p className="text-[10px] font-bold text-gray-400 uppercase mb-1">Risk Score</p>
                          <p className={`text-2xl font-black ${(result.osint_analysis.risk_score > 0.6) ? 'text-red-500' : (result.osint_analysis.risk_score > 0.3) ? 'text-yellow-500' : 'text-primary-500'}`}>
                            {(result.osint_analysis.risk_score * 100).toFixed(0)}<span className="text-xs font-bold text-gray-400">/100</span>
                          </p>
                        </div>
                        <div className="p-3 bg-gray-50 dark:bg-gray-900/40 rounded-xl border border-gray-100 dark:border-gray-800 shadow-inner">
                          <p className="text-[10px] font-bold text-gray-400 uppercase mb-1">Indicators</p>
                          <p className="text-2xl font-black text-gray-700 dark:text-gray-300">
                            {result.osint_analysis.reasons?.length || 0}
                          </p>
                        </div>
                      </div>

                      <div className="space-y-3 pt-2">
                        <p className="text-[10px] font-black uppercase text-gray-500 tracking-widest pl-1">Detailed Findings</p>
                        {result.osint_analysis.reasons?.length > 0 ? (
                          <div className="space-y-2">
                            {result.osint_analysis.reasons.map((ind: string, i: number) => (
                              <div key={i} className={`flex items-start gap-3 p-3 rounded-xl border transition-all duration-300 hover:scale-[1.01] ${
                                ind.startsWith('✓') 
                                  ? 'bg-green-50/50 border-green-100 dark:bg-green-900/10 dark:border-green-800/20 text-green-700 dark:text-green-400'
                                  : 'bg-white border-gray-100 dark:bg-gray-900/50 dark:border-gray-800 text-gray-800 dark:text-gray-200'
                              }`}>
                                <div className={`p-1 rounded-lg mt-0.5 ${ind.startsWith('✓') ? 'bg-green-500 text-white' : 'bg-primary-100 text-primary-600'}`}>
                                  {ind.startsWith('✓') ? <CheckCircle2 className="w-3 h-3" /> : <Info className="w-3 h-3" />}
                                </div>
                                <span className="text-sm font-medium">{ind}</span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="flex flex-col items-center justify-center py-6 text-green-600 dark:text-green-400 bg-green-50/30 dark:bg-green-900/10 rounded-2xl border border-green-100 dark:border-green-900/20">
                            <ShieldCheck className="w-8 h-8 mb-2 opacity-40" />
                            <p className="text-sm font-bold">Heuristic Analysis Clean</p>
                          </div>
                        )}
                      </div>
                    </>
                  ) : (
                    <div className="text-sm text-gray-400 text-center py-4 italic">
                      Technical breakdown unavailable for this scan.
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* ── Metadata Analysis Summary ───────────────────────────── */}
              {senderEmail && (
                <Card className="bg-gray-900 text-white border-none shadow-2xl overflow-hidden group">
                  <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                    <Globe className="w-32 h-32" />
                  </div>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs font-black uppercase tracking-widest text-primary-400">Security Fingerprint</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-y-4 gap-x-8 text-sm relative z-10">
                      <div>
                        <p className="text-[10px] font-bold text-gray-500 uppercase tracking-tighter">Originating Identity</p>
                        <p className="font-mono text-xs truncate text-primary-100">{senderEmail}</p>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold text-gray-500 uppercase tracking-tighter">Reputation Domain</p>
                        <p className="font-mono text-xs text-primary-100">{senderEmail.includes('@') ? senderEmail.split('@')[1] : '—'}</p>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold text-gray-500 uppercase tracking-tighter">TLD Context</p>
                        <p className="font-medium text-xs text-white">
                          {senderEmail.includes('@') ? '.' + senderEmail.split('@')[1].split('.').pop()?.toUpperCase() : '—'}
                        </p>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold text-gray-500 uppercase tracking-tighter">Security Stage</p>
                        <p className="font-medium text-xs text-white uppercase tracking-widest">{result.stage} LEVEL</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

            </div>
          )}
        </div>
      </div>
    </div>
  );
}
