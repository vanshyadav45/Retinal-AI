import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import RiskGauge from '../components/RiskGauge';

export default function ResultsPage({ result }) {
  const [view, setView] = useState('gradcam');

  const overlays = useMemo(
    () => ({
      gradcam: result?.gradcam_base64 ? `data:image/png;base64,${result.gradcam_base64}` : null,
      lesion: result?.lesion_base64 ? `data:image/png;base64,${result.lesion_base64}` : null,
      opticDisc: result?.optic_disc_base64 ? `data:image/png;base64,${result.optic_disc_base64}` : null
    }),
    [result]
  );

  const overlaySrc = overlays[view];
  const drStage = result?.dr_stage_label || `DR Grade ${result?.dr_grade ?? '-'}`;
  const glaucomaLabel = result?.glaucoma_label || (result?.glaucoma === 1 ? 'Glaucoma suspect' : 'Low glaucoma risk');
  const primaryDiagnosis = result?.primary_diagnosis || 'Pending clinical interpretation';
  const treatmentSuggestions = result?.treatment_suggestions || result?.next_steps || [];
  const predictions = result?.disease_predictions || [];
  const providers = result?.suggested_providers || [];

  if (!result) {
    return <div className="text-slate-500">Run an analysis from Upload & Analyze to view results.</div>;
  }

  const downloadOverlay = () => {
    if (!overlaySrc) return;
    const a = document.createElement('a');
    a.href = overlaySrc;
    a.download = `retinal_overlay_${view}.png`;
    a.click();
  };

  return (
    <section className="space-y-6 animate-rise">
      <h1 className="font-display text-3xl font-bold">Results</h1>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-100 bg-white p-4">
          <p className="text-sm font-semibold text-slate-600">Original</p>
          <img src={result.preview} alt="original" className="mt-2 max-h-[300px] w-full rounded-xl object-contain" />
        </div>
        <div className="rounded-2xl border border-slate-100 bg-white p-4">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-semibold text-slate-600">Overlay Viewer</p>
            <div className="flex gap-2">
              {[
                ['gradcam', 'Grad-CAM'],
                ['lesion', 'Lesion Mask'],
                ['opticDisc', 'Optic Disc']
              ].map(([key, label]) => (
                <button
                  key={key}
                  onClick={() => setView(key)}
                  className={`rounded-lg px-2 py-1 text-xs ${view === key ? 'bg-ink text-white' : 'bg-slate-100 text-slate-700'}`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
          {overlaySrc ? <img src={overlaySrc} alt="overlay" className="mt-2 max-h-[300px] w-full rounded-xl object-contain" /> : null}
          {view === 'gradcam' ? (
            <p className="mt-2 rounded-lg bg-ink/10 px-3 py-2 text-xs font-semibold text-ink">
              Grad-CAM is restricted to retinal eye area only. Non-retinal region is excluded from highlighting.
            </p>
          ) : null}
        </div>
      </div>

      <div className="rounded-2xl border border-slate-100 bg-white p-5">
        <h2 className="font-display text-xl font-semibold">Diagnosis Card</h2>
        <div className="mt-3 rounded-xl border border-accent/30 bg-accent/10 p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-600">Primary Diagnosis</p>
          <p className="mt-1 text-base font-semibold text-ink">{primaryDiagnosis}</p>
        </div>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <div className="rounded-xl bg-slate-50 p-3">DR Stage: <strong>{drStage}</strong></div>
          <div className="rounded-xl bg-slate-50 p-3">Glaucoma: <strong>{glaucomaLabel}</strong></div>
          <div className="rounded-xl bg-slate-50 p-3">CDR: <strong>{result.cdr}</strong></div>
          <div className="rounded-xl bg-slate-50 p-3">Confidence: <strong>{(result.confidence * 100).toFixed(1)}%</strong></div>
        </div>
        {predictions.length > 0 ? (
          <div className="mt-4 overflow-hidden rounded-xl border border-slate-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-3 py-2">Disease</th>
                  <th className="px-3 py-2">Prediction</th>
                  <th className="px-3 py-2">Severity</th>
                  <th className="px-3 py-2">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((item) => (
                  <tr className="border-t" key={item.disease}>
                    <td className="px-3 py-2">{item.disease}</td>
                    <td className="px-3 py-2">{item.status}</td>
                    <td className="px-3 py-2">{item.severity}</td>
                    <td className="px-3 py-2">{item.confidence_percent}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
        <div className="mt-4">
          <RiskGauge score={result.risk_score} />
        </div>
        <div className="mt-4 rounded-xl bg-slate-50 p-3">
          <p className="font-medium">Uncertainty (MC Dropout)</p>
          <p className="text-sm text-slate-600">Mean: {result.uncertainty_mean} | Std: {result.uncertainty_std}</p>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-100 bg-white p-5">
        <h2 className="font-display text-xl font-semibold">Easy-to-Understand Result</h2>
        <p className="mt-2 rounded-xl bg-slate-50 p-3 text-sm text-slate-700">{result.patient_summary}</p>

        <h3 className="mt-4 font-display text-lg font-semibold">What Exactly Was Scanned</h3>
        <div className="mt-2 grid gap-3 md:grid-cols-2">
          <div className="rounded-xl bg-slate-50 p-3 text-sm">
            <p className="font-medium">Analyzed Region</p>
            <p className="text-slate-700">{result.scan_details?.analyzed_region}</p>
          </div>
          <div className="rounded-xl bg-slate-50 p-3 text-sm">
            <p className="font-medium">Scanned Eye Area</p>
            <p className="text-slate-700">{result.scan_details?.scanned_area_percent}% of image</p>
          </div>
          <div className="rounded-xl bg-slate-50 p-3 text-sm">
            <p className="font-medium">Optic Disc Location</p>
            <p className="text-slate-700">
              Center: {result.scan_details?.optic_disc_center?.[0]}, {result.scan_details?.optic_disc_center?.[1]} | Radius: {result.scan_details?.optic_disc_radius}
            </p>
          </div>
          <div className="rounded-xl bg-slate-50 p-3 text-sm">
            <p className="font-medium">Detected Vessel Density</p>
            <p className="text-slate-700">{result.scan_details?.vessel_density_percent}%</p>
          </div>
        </div>

        <h3 className="mt-4 font-display text-lg font-semibold">Quality Checks Passed</h3>
        <div className="mt-2 rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
          Blur score: {result.scan_details?.quality_checks?.blur_score} | Brightness score: {result.scan_details?.quality_checks?.brightness_score} | Retinal eye detected: {String(result.scan_details?.quality_checks?.retinal_detected)}
        </div>

        <h3 className="mt-4 rounded-lg bg-danger/15 px-3 py-2 font-display text-lg font-extrabold text-danger">What You Should Do Next</h3>
        <div className="mt-2 grid gap-2">
          {result.next_steps?.map((step) => (
            <div key={step} className="suggestion-card suggestion-next">
              <p>{step}</p>
            </div>
          ))}
        </div>

        <h3 className="mt-4 rounded-lg bg-success/15 px-3 py-2 font-display text-lg font-extrabold text-success">Treatment Guidance</h3>
        <div className="mt-2 grid gap-2">
          {treatmentSuggestions.map((step) => (
            <div key={step} className="suggestion-card suggestion-treatment">
              <p>{step}</p>
            </div>
          ))}
        </div>

        <h3 className="mt-4 font-display text-lg font-semibold">Suggested Doctors & Hospitals</h3>
        {providers.length > 0 ? (
          <div className="mt-2 overflow-hidden rounded-xl border border-slate-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-3 py-2">Name</th>
                  <th className="px-3 py-2">Type</th>
                  <th className="px-3 py-2">City</th>
                  <th className="px-3 py-2">Contact</th>
                </tr>
              </thead>
              <tbody>
                {providers.map((p) => (
                  <tr className="border-t" key={`${p.type}-${p.name}`}>
                    <td className="px-3 py-2">{p.name}</td>
                    <td className="px-3 py-2">{p.type}</td>
                    <td className="px-3 py-2">{p.city}</td>
                    <td className="px-3 py-2">{p.contact}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="mt-2 text-sm text-slate-600">No provider suggestions available for this result.</p>
        )}
        <div className="mt-3">
          <Link to="/care" className="inline-flex rounded-lg bg-ink px-3 py-2 text-sm text-white">
            Open Full Care Navigator
          </Link>
        </div>

        <h3 className="mt-4 font-display text-lg font-semibold">Limitations</h3>
        <ul className="mt-2 list-disc space-y-1 pl-6 text-slate-700">
          {result.scan_details?.limitations?.map((lim) => <li key={lim}>{lim}</li>)}
        </ul>

        <h3 className="mt-4 font-display text-lg font-semibold">Detailed Clinical Notes</h3>
        <ul className="mt-3 list-disc space-y-1 pl-6 text-slate-700">
          {result.recommendations?.map((r) => <li key={r}>{r}</li>)}
        </ul>
        <div className="mt-4 overflow-hidden rounded-xl border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-3 py-2">Lesion Type</th>
                <th className="px-3 py-2">Color Code</th>
                <th className="px-3 py-2">Clinical Note</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-t"><td className="px-3 py-2">Hemorrhages</td><td className="px-3 py-2 text-red-600">Red</td><td className="px-3 py-2">Possible retinal bleeding burden</td></tr>
              <tr className="border-t"><td className="px-3 py-2">Hard Exudates</td><td className="px-3 py-2 text-yellow-600">Yellow</td><td className="px-3 py-2">Lipid leakage indicator</td></tr>
              <tr className="border-t"><td className="px-3 py-2">Microaneurysms</td><td className="px-3 py-2 text-blue-600">Blue</td><td className="px-3 py-2">Early DR vascular changes</td></tr>
              <tr className="border-t"><td className="px-3 py-2">Soft Exudates</td><td className="px-3 py-2 text-green-600">Green</td><td className="px-3 py-2">Nerve fiber ischemic change</td></tr>
            </tbody>
          </table>
        </div>
        <div className="mt-4 rounded-xl bg-ink/5 p-3 text-sm text-slate-700">
          Interpretation support: AI outputs are decision-support signals and should be correlated with ophthalmic examination and patient history.
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <button onClick={downloadOverlay} className="rounded-lg bg-ink px-3 py-2 text-sm text-white">Export Image</button>
          <a href="/reports" className="rounded-lg bg-accent px-3 py-2 text-sm font-medium text-ink">Export PDF</a>
        </div>
      </div>
    </section>
  );
}
