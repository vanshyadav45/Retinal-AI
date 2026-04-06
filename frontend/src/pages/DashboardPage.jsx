import { useEffect, useState } from 'react';
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import StatCard from '../components/StatCard';
import { fetchDashboard } from '../lib/api';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchDashboard().then(setStats).catch(() => setStats(null));
  }, []);

  const distribution = stats
    ? Object.entries(stats.disease_distribution).map(([k, v]) => ({ label: k.replace('_', ' ').toUpperCase(), value: v }))
    : [];

  const colors = ['#2a9d8f', '#fca311', '#e76f51', '#264653', '#d62828'];
  const riskBands = stats
    ? [
        { name: 'Low', value: (stats.total_scans || 0) - (stats.high_risk_cases || 0) },
        { name: 'High', value: stats.high_risk_cases || 0 }
      ]
    : [];

  return (
    <section className="space-y-6 animate-rise">
      <div className="hero-band rounded-3xl p-6 md:p-8">
        <h1 className="font-display text-3xl font-bold md:text-4xl">Clinical Intelligence Dashboard</h1>
        <p className="mt-2 max-w-2xl text-sm text-white/85 md:text-base">
          Real-time retinal triage insights with risk-focused monitoring for diabetic retinopathy and glaucoma.
        </p>
        <p className="mt-3 max-w-3xl text-xs text-white/80 md:text-sm">
          What this site does: You upload retinal eye images, AI checks for diabetic retinopathy and glaucoma risk,
          shows visual highlights, and generates a simple summary plus follow-up guidance.
        </p>
        <div className="mt-4 flex flex-wrap gap-2 text-xs text-white/85 md:text-sm">
          <span className="rounded-full bg-white/20 px-3 py-1">AI-Assisted Screening</span>
          <span className="rounded-full bg-white/20 px-3 py-1">Explainability Enabled</span>
          <span className="rounded-full bg-white/20 px-3 py-1">Rapid Report Workflow</span>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard title="Total Scans" value={stats?.total_scans ?? 0} />
        <StatCard title="High Risk Cases" value={stats?.high_risk_cases ?? 0} tone="danger" />
        <StatCard title="Alerts" value={(stats?.high_risk_cases ?? 0) > 0 ? 'Active' : 'Stable'} tone="accent" />
      </div>

      {(stats?.high_risk_cases ?? 0) > 0 ? (
        <div className="rounded-2xl border border-danger/20 bg-danger/10 p-4 text-danger">
          High-risk alert: {(stats?.high_risk_cases ?? 0)} cases require accelerated specialist review.
        </div>
      ) : (
        <div className="rounded-2xl border border-success/20 bg-success/10 p-4 text-success">
          No critical spikes detected in the recent scan window.
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="glass-panel rounded-2xl p-4">
          <h2 className="font-display text-lg font-semibold">Activity Timeline</h2>
          <div className="mt-3 h-64">
            <ResponsiveContainer>
              <AreaChart data={stats?.timeline ?? []}>
                <defs>
                  <linearGradient id="timelineFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#14213d" stopOpacity={0.6} />
                    <stop offset="95%" stopColor="#14213d" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" />
                <YAxis />
                <CartesianGrid strokeDasharray="3 3" />
                <Tooltip />
                <Area type="monotone" dataKey="count" stroke="#14213d" fill="url(#timelineFill)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-4">
          <h2 className="font-display text-lg font-semibold">Disease Distribution</h2>
          <div className="mt-3 h-64">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={distribution} dataKey="value" nameKey="label" outerRadius={90}>
                  {distribution.map((entry, idx) => (
                    <Cell key={entry.label} fill={colors[idx % colors.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="glass-panel rounded-2xl p-4">
          <h2 className="font-display text-lg font-semibold">How It Works</h2>
          <ol className="mt-3 list-decimal space-y-2 pl-6 text-sm text-slate-700">
            <li>Upload only retinal eye images.</li>
            <li>System runs quality checks and validates that image is eye fundus.</li>
            <li>AI predicts disease risk and creates visual overlays.</li>
            <li>You get patient-friendly summary and next steps.</li>
          </ol>
        </div>

        <div className="glass-panel rounded-2xl p-4">
          <h2 className="font-display text-lg font-semibold">Risk Band Overview</h2>
          <div className="mt-3 h-56">
            <ResponsiveContainer>
              <BarChart data={riskBands}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#14213d" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </section>
  );
}
