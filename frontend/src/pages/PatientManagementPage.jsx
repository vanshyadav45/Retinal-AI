import { useEffect, useState } from 'react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { createPatient, fetchPatientHistory, fetchPatients } from '../lib/api';

export default function PatientManagementPage() {
  const [patients, setPatients] = useState([]);
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState(null);
  const [history, setHistory] = useState([]);
  const [form, setForm] = useState({ patient_code: '', full_name: '', age: 50, sex: 'F' });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const loadPatients = async () => setPatients(await fetchPatients());

  useEffect(() => {
    loadPatients().catch(() => setPatients([]));
  }, []);

  const selectPatient = async (patient) => {
    setSelected(patient);
    setHistory(await fetchPatientHistory(patient.id));
  };

  const submit = async () => {
    setMessage('');
    setError('');
    try {
      await createPatient({ ...form, age: Number(form.age) });
      setForm({ patient_code: '', full_name: '', age: 50, sex: 'F' });
      setMessage('Patient added successfully. You can now select this patient on Upload & Analyze.');
      await loadPatients();
    } catch (e) {
      setError(e?.response?.data?.detail || 'Unable to create patient.');
    }
  };

  const filtered = patients.filter((p) => `${p.patient_code} ${p.full_name}`.toLowerCase().includes(query.toLowerCase()));

  return (
    <section className="space-y-5 animate-rise">
      <h1 className="font-display text-3xl font-bold">Patient Management</h1>
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="rounded-2xl border border-slate-100 bg-white p-4 lg:col-span-1">
          <h2 className="font-display text-lg font-semibold">Add Patient</h2>
          <div className="mt-3 space-y-2">
            <input placeholder="Code" value={form.patient_code} onChange={(e) => setForm({ ...form, patient_code: e.target.value })} className="w-full rounded-lg border px-3 py-2" />
            <input placeholder="Full Name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} className="w-full rounded-lg border px-3 py-2" />
            <input type="number" placeholder="Age" value={form.age} onChange={(e) => setForm({ ...form, age: e.target.value })} className="w-full rounded-lg border px-3 py-2" />
            <select value={form.sex} onChange={(e) => setForm({ ...form, sex: e.target.value })} className="w-full rounded-lg border px-3 py-2">
              <option value="F">Female</option>
              <option value="M">Male</option>
              <option value="Other">Other</option>
            </select>
            <button onClick={submit} className="w-full rounded-lg bg-ink px-3 py-2 text-white">Save Patient</button>
            {message ? <p className="text-xs text-green-700">{message}</p> : null}
            {error ? <p className="text-xs text-danger">{error}</p> : null}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-100 bg-white p-4 lg:col-span-2">
          <input placeholder="Search patients" value={query} onChange={(e) => setQuery(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
          <div className="mt-3 max-h-64 overflow-auto rounded-xl border">
            {filtered.map((p) => (
              <button key={p.id} onClick={() => selectPatient(p)} className="flex w-full items-center justify-between border-b px-3 py-2 text-left hover:bg-slate-50">
                <span>{p.patient_code} - {p.full_name}</span>
                <span className="text-xs text-slate-500">{p.sex}, {p.age}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-100 bg-white p-4">
        <h2 className="font-display text-lg font-semibold">Disease Progression</h2>
        <p className="text-sm text-slate-500">{selected ? selected.full_name : 'Select a patient to view history'}</p>
        <div className="mt-3 h-64">
          <ResponsiveContainer>
            <LineChart data={history.map((h) => ({ ...h, date: new Date(h.created_at).toLocaleDateString() })).reverse()}>
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="risk_score" stroke="#d62828" />
              <Line type="monotone" dataKey="cdr" stroke="#14213d" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-3 space-y-2">
          {history.length === 0 ? <p className="text-sm text-slate-500">No scans found for this patient yet.</p> : null}
          {history.slice(0, 4).map((item) => (
            <div key={item.scan_id} className="rounded-lg border border-slate-200 p-3 text-sm">
              <p className="font-medium">Scan #{item.scan_id} - Risk {Number(item.risk_score).toFixed(1)}/100</p>
              <p className="text-slate-600">{item.summary}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
