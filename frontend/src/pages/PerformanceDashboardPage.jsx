import { useEffect, useMemo, useState } from 'react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import StatCard from '../components/StatCard';
import { fetchMetrics } from '../lib/api';

export default function PerformanceDashboardPage() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    fetchMetrics().then(setMetrics).catch(() => setMetrics(null));
  }, []);

  const confusionText = useMemo(() => {
    if (!metrics) return 'No confusion matrix data';
    return metrics.confusion_matrix.map((row) => row.join(' | ')).join(' / ');
  }, [metrics]);

  return (
    <section className="space-y-5 animate-rise">
      <h1 className="font-display text-3xl font-bold">Model Performance</h1>

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard title="AUC ROC" value={metrics?.auc_roc ?? '-'} />
        <StatCard title="QWK" value={metrics?.qwk ?? '-'} tone="accent" />
        <StatCard title="F1 Score" value={metrics?.f1_score ?? '-'} tone="success" />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {[
          ['ROC Curve', metrics?.roc_curve, '#14213d'],
          ['PR Curve', metrics?.pr_curve, '#fca311'],
          ['Calibration Curve', metrics?.calibration_curve, '#2a9d8f']
        ].map(([title, data, color]) => (
          <div className="rounded-2xl border border-slate-100 bg-white p-4" key={title}>
            <h2 className="font-display text-lg font-semibold">{title}</h2>
            <div className="mt-2 h-56">
              <ResponsiveContainer>
                <LineChart data={data || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="x" />
                  <YAxis dataKey="y" />
                  <Tooltip />
                  <Line type="monotone" dataKey="y" stroke={color} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-2xl border border-slate-100 bg-white p-4">
        <h2 className="font-display text-lg font-semibold">Confusion Matrix</h2>
        <p className="mt-2 rounded-xl bg-slate-50 p-3 font-mono text-sm">{confusionText}</p>
      </div>
    </section>
  );
}
