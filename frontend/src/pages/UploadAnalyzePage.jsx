import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { analyzeImage, fetchPatients } from '../lib/api';

export default function UploadAnalyzePage({ onResult }) {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [mode, setMode] = useState('combined');
  const [patients, setPatients] = useState([]);
  const [patientId, setPatientId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPatients().then((list) => {
      setPatients(list);
      const stored = localStorage.getItem('retinalai_selected_patient_id');
      if (stored) {
        setPatientId(stored);
      }
    }).catch(() => setPatients([]));
  }, []);

  const onPick = (picked) => {
    setFile(picked);
    setPreview(URL.createObjectURL(picked));
    setError('');
  };

  const submit = async () => {
    if (!file) {
      setError('Please upload a retinal image first.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const result = await analyzeImage({ file, mode, patientId: patientId ? Number(patientId) : undefined });
      if (patientId) {
        localStorage.setItem('retinalai_selected_patient_id', patientId);
      }
      onResult({ ...result, preview });
      navigate('/results');
    } catch (e) {
      setError(e?.response?.data?.detail || 'Analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-5 animate-rise">
      <h1 className="font-display text-3xl font-bold">Upload and Analyze</h1>
      <div className="grid gap-3 md:grid-cols-3">
        <div className="glass-panel rounded-2xl p-4">
          <p className="text-xs font-semibold uppercase text-slate-500">Step 1</p>
          <p className="mt-1 font-display text-lg font-semibold">Upload Fundus Scan</p>
          <p className="mt-1 text-sm soft-text">PNG/JPG with clear optic disc visibility is recommended.</p>
        </div>
        <div className="glass-panel rounded-2xl p-4">
          <p className="text-xs font-semibold uppercase text-slate-500">Step 2</p>
          <p className="mt-1 font-display text-lg font-semibold">AI Multi-task Analysis</p>
          <p className="mt-1 text-sm soft-text">DR grading, glaucoma risk, CDR estimate, and uncertainty profiling.</p>
        </div>
        <div className="glass-panel rounded-2xl p-4">
          <p className="text-xs font-semibold uppercase text-slate-500">Step 3</p>
          <p className="mt-1 font-display text-lg font-semibold">Clinical Output</p>
          <p className="mt-1 text-sm soft-text">Explainability overlays and report-ready structured findings.</p>
        </div>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border-2 border-dashed border-ink/25 p-6">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => e.target.files?.[0] && onPick(e.target.files[0])}
            className="w-full rounded-lg border border-slate-200 px-3 py-2"
          />
          <p className="mt-2 text-sm text-slate-500">Quality checks: blur and brightness are validated server-side.</p>
          <div className="mt-4">
            <label className="text-sm font-medium">Patient (Recommended)</label>
            <select
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
            >
              <option value="">No patient selected</option>
              {patients.map((p) => (
                <option key={p.id} value={p.id}>{p.patient_code} - {p.full_name}</option>
              ))}
            </select>
          </div>
          <div className="mt-4">
            <label className="text-sm font-medium">Disease Mode</label>
            <select value={mode} onChange={(e) => setMode(e.target.value)} className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2">
              <option value="combined">Combined DR + Glaucoma</option>
              <option value="dr">DR only</option>
              <option value="glaucoma">Glaucoma only</option>
            </select>
          </div>
          <button onClick={submit} disabled={loading} className="mt-4 rounded-xl bg-ink px-4 py-2 font-medium text-white disabled:opacity-60">
            {loading ? 'Analyzing...' : 'Submit for Analysis'}
          </button>
          {error && <p className="mt-3 text-sm text-danger">{error}</p>}
        </div>

        <div className="rounded-2xl border border-slate-100 bg-white p-4">
          <h2 className="font-display text-lg font-semibold">Image Preview</h2>
          {preview ? (
            <img src={preview} alt="preview" className="mt-3 max-h-[340px] w-full rounded-xl object-contain" />
          ) : (
            <div className="mt-3 flex h-[300px] items-center justify-center rounded-xl bg-slate-50 text-slate-400">No image selected</div>
          )}
          <div className="mt-3 rounded-xl bg-slate-50 p-3 text-xs text-slate-600">
            Quality policy: automatic blur and brightness validation is enforced before model inference.
          </div>
        </div>
      </div>
    </section>
  );
}
