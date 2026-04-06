import axios from 'axios';

const fallbackBase = typeof window !== 'undefined' ? `${window.location.origin}/api` : 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || fallbackBase,
  timeout: 30000
});

const isObject = (value) => value && typeof value === 'object' && !Array.isArray(value);

export const fetchDashboard = async () => {
  const data = (await api.get('/dashboard/stats')).data;
  if (!isObject(data)) {
    return {
      total_scans: 0,
      high_risk_cases: 0,
      disease_distribution: {},
      timeline: []
    };
  }
  return {
    total_scans: Number(data.total_scans || 0),
    high_risk_cases: Number(data.high_risk_cases || 0),
    disease_distribution: isObject(data.disease_distribution) ? data.disease_distribution : {},
    timeline: Array.isArray(data.timeline) ? data.timeline : []
  };
};

export const fetchPatients = async () => {
  const data = (await api.get('/patients')).data;
  return Array.isArray(data) ? data : [];
};
export const createPatient = async (payload) => (await api.post('/patients', payload)).data;
export const fetchPatientHistory = async (id) => (await api.get(`/patients/${id}/history`)).data;
export const fetchMetrics = async () => (await api.get('/model/metrics')).data;
export const generateReport = async (scanId) => (await api.post('/report/generate', { scan_id: scanId })).data;
export const fetchCareProviders = async (city) => {
  const params = city ? { city } : undefined;
  return (await api.get('/care/providers', { params })).data;
};

export const analyzeImage = async ({ file, patientId, mode }) => {
  const form = new FormData();
  form.append('image', file);
  if (patientId) form.append('patient_id', String(patientId));
  form.append('mode', mode || 'combined');
  return (await api.post('/analyze', form, { headers: { 'Content-Type': 'multipart/form-data' } })).data;
};

export default api;
