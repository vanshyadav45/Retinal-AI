import { Navigate, Route, Routes } from 'react-router-dom';
import { useMemo, useState } from 'react';

import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import PatientManagementPage from './pages/PatientManagementPage';
import PerformanceDashboardPage from './pages/PerformanceDashboardPage';
import CareNavigatorPage from './pages/CareNavigatorPage';
import ReportGeneratorPage from './pages/ReportGeneratorPage';
import ResultsPage from './pages/ResultsPage';
import UploadAnalyzePage from './pages/UploadAnalyzePage';

export default function App() {
  const [latestResult, setLatestResult] = useState(() => {
    try {
      const saved = localStorage.getItem('retinalai_latest_result');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const onSetLatestResult = useMemo(
    () => (value) => {
      setLatestResult(value);
      try {
        localStorage.setItem('retinalai_latest_result', JSON.stringify(value));
      } catch {
        // Ignore storage failures.
      }
    },
    []
  );

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/analyze" element={<UploadAnalyzePage onResult={onSetLatestResult} />} />
        <Route path="/results" element={<ResultsPage result={latestResult} />} />
        <Route path="/care" element={<CareNavigatorPage result={latestResult} />} />
        <Route path="/patients" element={<PatientManagementPage />} />
        <Route path="/performance" element={<PerformanceDashboardPage />} />
        <Route path="/reports" element={<ReportGeneratorPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
