import { useState } from 'react';

import { generateReport } from '../lib/api';

export default function ReportGeneratorPage() {
  const [scanId, setScanId] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const onGenerate = async () => {
    setError('');
    setResult(null);
    try {
      const data = await generateReport(Number(scanId));
      setResult(data);
    } catch (e) {
      setError(e?.response?.data?.detail || 'Report generation failed.');
    }
  };

  return (
    <section className="space-y-5 animate-rise">
      <h1 className="font-display text-3xl font-bold">Report Generator</h1>
      <div className="max-w-xl rounded-2xl border border-slate-100 bg-white p-5">
        <label className="text-sm font-medium">Scan ID</label>
        <input value={scanId} onChange={(e) => setScanId(e.target.value)} type="number" className="mt-1 w-full rounded-lg border px-3 py-2" />
        <button onClick={onGenerate} className="mt-4 rounded-xl bg-ink px-4 py-2 text-white">Generate Medical PDF</button>
        {result && (
          <div className="mt-4 rounded-lg bg-slate-50 p-3 text-sm">
            <p>Report ID: {result.report_id}</p>
            <p>Path: {result.report_path}</p>
          </div>
        )}
        {error && <p className="mt-3 text-sm text-danger">{error}</p>}
      </div>
    </section>
  );
}
