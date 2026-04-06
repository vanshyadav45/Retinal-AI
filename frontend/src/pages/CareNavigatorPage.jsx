import { useEffect, useMemo, useState } from 'react';

import { fetchCareProviders } from '../lib/api';

export default function CareNavigatorPage({ result }) {
  const [city, setCity] = useState('');
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadProviders = async (selectedCity = '') => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchCareProviders(selectedCity || undefined);
      setProviders(data);
    } catch {
      setError('Unable to load doctor and hospital directory right now.');
      setProviders([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProviders();
  }, []);

  const treatmentSuggestions = useMemo(() => {
    if (result?.treatment_suggestions?.length) {
      return result.treatment_suggestions;
    }
    return [
      'Book a comprehensive eye exam with dilated fundoscopy.',
      'Keep blood sugar and blood pressure controlled with your physician support.',
      'Do not start or stop eye medication without specialist advice.',
      'Repeat retinal imaging according to ophthalmologist follow-up plan.',
    ];
  }, [result]);

  const diagnosisSummary = result?.primary_diagnosis || 'No latest analysis found. Run Upload & Analyze to get patient-specific guidance.';

  return (
    <section className="space-y-6 animate-rise">
      <h1 className="font-display text-3xl font-bold">Care Navigator</h1>
      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Current Case Summary</p>
        <p className="mt-2 text-base font-medium text-ink">{diagnosisSummary}</p>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <div className="rounded-xl bg-slate-50 p-3 text-sm">
            <p className="font-medium">DR Stage</p>
            <p>{result?.dr_stage_label || 'N/A'}</p>
          </div>
          <div className="rounded-xl bg-slate-50 p-3 text-sm">
            <p className="font-medium">Glaucoma Status</p>
            <p>{result?.glaucoma_label || 'N/A'}</p>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <h2 className="font-display text-xl font-semibold">Detailed Treatment Guidance</h2>
        <ul className="mt-3 list-disc space-y-2 pl-6 text-slate-700">
          {treatmentSuggestions.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <label className="text-sm font-medium">Filter by City</label>
            <input
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="Delhi / Bengaluru / Mumbai"
              className="mt-1 w-72 rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <button
            onClick={() => loadProviders(city.trim())}
            className="rounded-lg bg-ink px-3 py-2 text-sm text-white"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Search Providers'}
          </button>
          <button
            onClick={() => {
              setCity('');
              loadProviders('');
            }}
            className="rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-700"
          >
            Clear
          </button>
        </div>

        {error ? <p className="mt-3 text-sm text-danger">{error}</p> : null}

        <div className="mt-4 overflow-hidden rounded-xl border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-3 py-2">Name</th>
                <th className="px-3 py-2">Type</th>
                <th className="px-3 py-2">City</th>
                <th className="px-3 py-2">Specialties</th>
                <th className="px-3 py-2">Contact</th>
                <th className="px-3 py-2">Address</th>
                <th className="px-3 py-2">Notes</th>
              </tr>
            </thead>
            <tbody>
              {providers.map((p) => (
                <tr className="border-t" key={`${p.type}-${p.name}-${p.city}`}>
                  <td className="px-3 py-2">{p.name}</td>
                  <td className="px-3 py-2">{p.type}</td>
                  <td className="px-3 py-2">{p.city}</td>
                  <td className="px-3 py-2">{(p.specialties || []).join(', ')}</td>
                  <td className="px-3 py-2">{p.contact}</td>
                  <td className="px-3 py-2">{p.address}</td>
                  <td className="px-3 py-2">{p.notes}</td>
                </tr>
              ))}
              {!loading && providers.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-3 py-6 text-center text-slate-500">
                    No providers found for selected city.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
