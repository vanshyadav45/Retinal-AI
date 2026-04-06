export default function StatCard({ title, value, tone = 'ink' }) {
  const colorMap = {
    ink: 'text-ink border-ink/20 bg-ink/5',
    danger: 'text-danger border-danger/35 bg-danger/10',
    success: 'text-success border-success/35 bg-success/10',
    accent: 'text-accent border-accent/35 bg-accent/10'
  };

  return (
    <div className={`rounded-2xl border p-4 shadow-sm ${colorMap[tone]}`}>
      <p className="text-sm font-semibold uppercase tracking-wide text-slate-600">{title}</p>
      <p className="mt-2 text-3xl font-extrabold">{value}</p>
    </div>
  );
}
