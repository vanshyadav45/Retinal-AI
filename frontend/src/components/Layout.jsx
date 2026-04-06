import { Activity, Brain, FileText, Gauge, HeartPulse, UploadCloud, Users } from 'lucide-react';
import { Link, NavLink } from 'react-router-dom';

const links = [
  { to: '/', label: 'Dashboard', icon: Gauge },
  { to: '/analyze', label: 'Upload & Analyze', icon: UploadCloud },
  { to: '/results', label: 'Results', icon: Brain },
  { to: '/care', label: 'Care Navigator', icon: HeartPulse },
  { to: '/patients', label: 'Patient Management', icon: Users },
  { to: '/performance', label: 'Model Performance', icon: Activity },
  { to: '/reports', label: 'Report Generator', icon: FileText }
];

export default function Layout({ children }) {
  const backendUrl = import.meta.env.VITE_API_URL;
  const showBackendWarning = typeof window !== 'undefined' && !backendUrl;

  return (
    <div className="retinal-bg min-h-screen p-4 md:p-8">
      <div className="mx-auto grid max-w-7xl gap-6 md:grid-cols-[260px_1fr]">
        <aside className="rounded-3xl border border-white/40 bg-white/80 p-5 shadow-glow backdrop-blur">
          <Link to="/" className="font-display text-2xl font-bold text-ink">
            RetinalAI
          </Link>
          <p className="mt-2 text-sm text-slate-500">Automated Eye Disease Diagnosis</p>
          <nav className="mt-6 flex flex-col gap-2">
            {links.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition ${
                      isActive ? 'bg-ink text-white' : 'text-slate-700 hover:bg-slate-100'
                    }`
                  }
                >
                  <Icon size={16} />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
          {showBackendWarning ? (
            <div className="mt-6 rounded-2xl border border-success/30 bg-success/10 p-3 text-xs text-success">
              Self-contained demo mode is active. The app will use browser data and built-in clinical placeholders, so you can redeploy the frontend without a separate backend.
            </div>
          ) : null}
        </aside>
        <main className="rounded-3xl border border-white/40 bg-white/92 p-5 shadow-glow backdrop-blur md:p-8">{children}</main>
      </div>
    </div>
  );
}
