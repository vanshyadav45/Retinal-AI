import axios from 'axios';
import {
  buildDemoAnalysis,
  getDemoDashboard,
  getDemoHistory,
  getDemoMetrics,
  getDemoPatients,
  getDemoProviders
} from './demoData';

const fallbackBase = typeof window !== 'undefined' ? `${window.location.origin}/api` : 'http://127.0.0.1:8000/api';
const hasLiveApi = Boolean(import.meta.env.VITE_API_URL);
const patientStoreKey = 'retinalai_demo_patients';
const historyStoreKey = 'retinalai_demo_history';
const analysisStoreKey = 'retinalai_demo_analyses';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || fallbackBase,
  timeout: 30000
});

const isObject = (value) => value && typeof value === 'object' && !Array.isArray(value);
const safeArray = (value) => (Array.isArray(value) ? value : []);
const safeObject = (value, fallback = {}) => (isObject(value) ? value : fallback);

const defaultMetrics = {
  auc_roc: '-',
  qwk: '-',
  f1_score: '-',
  roc_curve: [],
  pr_curve: [],
  calibration_curve: [],
  confusion_matrix: []
};

const defaultAnalysis = {
  primary_diagnosis: 'Analysis unavailable',
  dr_stage_label: 'N/A',
  glaucoma_label: 'N/A',
  disease_predictions: [],
  treatment_suggestions: [],
  suggested_providers: [],
  next_steps: [],
  recommendations: [],
  scan_details: {
    analyzed_region: 'Retinal fundus',
    scanned_area_percent: 0,
    optic_disc_center: [0, 0],
    optic_disc_radius: 0,
    vessel_density_percent: 0,
    quality_checks: {
      blur_score: 0,
      brightness_score: 0,
      retinal_detected: false
    },
    limitations: []
  }
};

const readJson = (key, fallback) => {
  if (typeof window === 'undefined') return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
};

const writeJson = (key, value) => {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Ignore browser storage limits.
  }
};

const getStoredPatients = () => {
  const stored = readJson(patientStoreKey, null);
  return Array.isArray(stored) && stored.length > 0 ? stored : getDemoPatients();
};

const getStoredHistory = () => readJson(historyStoreKey, {});

const getStoredAnalyses = () => readJson(analysisStoreKey, []);

const persistAnalysis = (analysis, patientId) => {
  const analyses = getStoredAnalyses();
  analyses.unshift({
    ...analysis,
    patient_id: patientId || null,
    created_at: new Date().toISOString()
  });
  writeJson(analysisStoreKey, analyses.slice(0, 20));

  if (!patientId) return;
  const history = getStoredHistory();
  const patientHistory = Array.isArray(history[patientId]) ? history[patientId] : getDemoHistory(Number(patientId));
  history[patientId] = [
    {
      scan_id: analysis.id || Date.now(),
      created_at: new Date().toISOString(),
      risk_score: analysis.risk_score,
      cdr: analysis.cdr,
      summary: analysis.patient_summary
    },
    ...patientHistory
  ].slice(0, 10);
  writeJson(historyStoreKey, history);
};

const buildOfflineMetrics = () => {
  const analyses = getStoredAnalyses();
  if (analyses.length === 0) return getDemoMetrics();
  const highRiskCases = analyses.filter((item) => Number(item.risk_score || 0) >= 60).length;
  return {
    ...getDemoMetrics(),
    auc_roc: Number((0.7 + Math.min(0.15, analyses.length / 300)).toFixed(2)),
    qwk: Number((0.12 + Math.min(0.1, analyses.length / 500)).toFixed(2)),
    f1_score: Number((0.36 + Math.min(0.12, analyses.length / 250)).toFixed(2)),
    confusion_matrix: [
      [Math.max(10, analyses.length + 4), 3, 1],
      [4, Math.max(8, highRiskCases + 6), 2],
      [1, 2, Math.max(4, Math.floor(analyses.length / 4))]
    ]
  };
};

export const fetchDashboard = async () => {
  if (!hasLiveApi) {
    const analyses = getStoredAnalyses();
    if (analyses.length === 0) return getDemoDashboard();
    const highRiskCases = analyses.filter((item) => Number(item.risk_score || 0) >= 60).length;
    return {
      total_scans: analyses.length,
      high_risk_cases: highRiskCases,
      disease_distribution: {
        no_dr: Math.max(0, analyses.length - highRiskCases - 4),
        mild_dr: Math.max(1, Math.floor(analyses.length / 4)),
        moderate_dr: Math.max(1, Math.floor(analyses.length / 5)),
        severe_dr: Math.max(1, Math.floor(highRiskCases / 3)),
        glaucoma_suspect: Math.max(1, Math.floor(highRiskCases / 4))
      },
      timeline: getDemoDashboard().timeline
    };
  }
  const data = (await api.get('/dashboard/stats')).data;
  if (!isObject(data)) return getDemoDashboard();
  return {
    total_scans: Number(data.total_scans || 0),
    high_risk_cases: Number(data.high_risk_cases || 0),
    disease_distribution: isObject(data.disease_distribution) ? data.disease_distribution : {},
    timeline: Array.isArray(data.timeline) ? data.timeline : []
  };
};

export const fetchPatients = async () => {
  if (!hasLiveApi) return getStoredPatients();
  const data = (await api.get('/patients')).data;
  return safeArray(data);
};

export const createPatient = async (payload) => {
  if (!hasLiveApi) {
    const patients = getStoredPatients();
    const nextId = patients.reduce((maxId, patient) => Math.max(maxId, Number(patient.id || 0)), 0) + 1;
    const created = {
      id: nextId,
      patient_code: String(payload.patient_code || `P-${1000 + nextId}`),
      full_name: String(payload.full_name || 'Demo Patient'),
      age: Number(payload.age || 50),
      sex: payload.sex || 'F'
    };
    const updated = [created, ...patients];
    writeJson(patientStoreKey, updated);
    return created;
  }
  return safeObject((await api.post('/patients', payload)).data);
};

export const fetchPatientHistory = async (id) => {
  if (!hasLiveApi) {
    const history = getStoredHistory();
    return safeArray(history[id] || getDemoHistory(Number(id)));
  }
  return safeArray((await api.get(`/patients/${id}/history`)).data);
};

export const fetchMetrics = async () => {
  if (!hasLiveApi) return buildOfflineMetrics();
  return safeObject((await api.get('/model/metrics')).data, defaultMetrics);
};

export const generateReport = async (scanId) => {
  if (!hasLiveApi) {
    return {
      report_id: `demo-${scanId}`,
      status: 'ready',
      summary: 'Offline demo report generated from local browser data.',
      scan_id: scanId
    };
  }
  return safeObject((await api.post('/report/generate', { scan_id: scanId })).data);
};

export const fetchCareProviders = async (city) => {
  if (!hasLiveApi) return getDemoProviders(city);
  const params = city ? { city } : undefined;
  return safeArray((await api.get('/care/providers', { params })).data);
};

export const analyzeImage = async ({ file, patientId, mode }) => {
  if (!hasLiveApi) {
    const result = buildDemoAnalysis({ file, patientId, mode });
    persistAnalysis(result, patientId);
    return result;
  }
  const form = new FormData();
  form.append('image', file);
  if (patientId) form.append('patient_id', String(patientId));
  form.append('mode', mode || 'combined');
  const data = safeObject((await api.post('/analyze', form, { headers: { 'Content-Type': 'multipart/form-data' } })).data, defaultAnalysis);
  return {
    ...defaultAnalysis,
    ...data,
    disease_predictions: safeArray(data.disease_predictions),
    treatment_suggestions: safeArray(data.treatment_suggestions),
    suggested_providers: safeArray(data.suggested_providers),
    next_steps: safeArray(data.next_steps),
    recommendations: safeArray(data.recommendations),
    scan_details: {
      ...defaultAnalysis.scan_details,
      ...safeObject(data.scan_details),
      quality_checks: {
        ...defaultAnalysis.scan_details.quality_checks,
        ...safeObject(data.scan_details?.quality_checks)
      },
      limitations: safeArray(data.scan_details?.limitations)
    }
  };
};

export default api;
