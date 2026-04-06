export default function RiskGauge({ score }) {
  const pct = Math.max(0, Math.min(100, score ?? 0));
  const hue = pct < 40 ? '#2a9d8f' : pct < 70 ? '#fca311' : '#d62828';

  return (
    <div className="space-y-2">
      <div className="h-5 w-full overflow-hidden rounded-full border border-slate-300 bg-slate-200">
        <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: `linear-gradient(90deg, ${hue}, #14213d)` }} />
      </div>
      <p className="text-sm font-extrabold tracking-wide text-slate-800">Risk Score: {pct.toFixed(2)} / 100</p>
    </div>
  );
}
