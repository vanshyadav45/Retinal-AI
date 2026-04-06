const demoProviders = [
  {
    name: 'Retina Care Institute',
    type: 'Hospital',
    city: 'Delhi',
    specialties: ['Retina', 'Diabetic Eye Disease'],
    contact: '+91 11 4000 1200',
    address: 'Connaught Place, New Delhi',
    notes: 'Book a retina specialist review within 1 week.'
  },
  {
    name: 'VisionPlus Eye Hospital',
    type: 'Hospital',
    city: 'Bengaluru',
    specialties: ['Glaucoma', 'Retina'],
    contact: '+91 80 4100 2211',
    address: 'Indiranagar, Bengaluru',
    notes: 'Supports imaging, IOP checks, and follow-up care.'
  },
  {
    name: 'Dr. Asha Menon',
    type: 'Doctor',
    city: 'Mumbai',
    specialties: ['Ophthalmology', 'Retina'],
    contact: '+91 22 4022 5588',
    address: 'Andheri East, Mumbai',
    notes: 'Ideal for detailed diabetic retinopathy evaluation.'
  }
];

const demoMetrics = {
  auc_roc: 0.81,
  qwk: 0.19,
  f1_score: 0.44,
  roc_curve: [
    { x: 0, y: 0 },
    { x: 0.2, y: 0.46 },
    { x: 0.5, y: 0.71 },
    { x: 0.8, y: 0.89 },
    { x: 1, y: 1 }
  ],
  pr_curve: [
    { x: 0, y: 1 },
    { x: 0.25, y: 0.82 },
    { x: 0.5, y: 0.64 },
    { x: 0.75, y: 0.49 },
    { x: 1, y: 0.31 }
  ],
  calibration_curve: [
    { x: 0, y: 0.05 },
    { x: 0.25, y: 0.24 },
    { x: 0.5, y: 0.48 },
    { x: 0.75, y: 0.69 },
    { x: 1, y: 0.9 }
  ],
  confusion_matrix: [
    [28, 3, 1],
    [4, 17, 2],
    [1, 2, 12]
  ]
};

const demoDashboard = {
  total_scans: 48,
  high_risk_cases: 14,
  disease_distribution: {
    no_dr: 22,
    mild_dr: 11,
    moderate_dr: 8,
    severe_dr: 4,
    glaucoma_suspect: 3
  },
  timeline: [
    { date: 'Mon', count: 5 },
    { date: 'Tue', count: 8 },
    { date: 'Wed', count: 6 },
    { date: 'Thu', count: 12 },
    { date: 'Fri', count: 9 },
    { date: 'Sat', count: 4 },
    { date: 'Sun', count: 4 }
  ]
};

const demoPatients = [
  { id: 1, patient_code: 'P-1001', full_name: 'Anika Sharma', age: 52, sex: 'F' },
  { id: 2, patient_code: 'P-1002', full_name: 'Rahul Mehta', age: 61, sex: 'M' }
];

const demoHistory = {
  1: [
    { scan_id: 1001, created_at: '2026-03-18T09:30:00Z', risk_score: 62, cdr: 0.46, summary: 'Moderate retinopathy signs with close follow-up suggested.' },
    { scan_id: 1008, created_at: '2026-04-02T11:15:00Z', risk_score: 74, cdr: 0.49, summary: 'Risk is increasing; specialist review is recommended.' }
  ],
  2: [
    { scan_id: 1002, created_at: '2026-03-29T08:20:00Z', risk_score: 31, cdr: 0.32, summary: 'Low-risk profile with routine monitoring.' }
  ]
};

const toBase64 = (value) => {
  if (typeof window !== 'undefined' && typeof window.btoa === 'function') {
    return window.btoa(unescape(encodeURIComponent(value)));
  }
  return Buffer.from(value, 'utf-8').toString('base64');
};

const makeOverlay = (title, accent) => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="900" height="600" viewBox="0 0 900 600">
      <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#08111f" />
          <stop offset="100%" stop-color="#1f2f4a" />
        </linearGradient>
        <radialGradient id="retina" cx="50%" cy="50%" r="55%">
          <stop offset="0%" stop-color="#f5efe1" stop-opacity="0.98" />
          <stop offset="70%" stop-color="#e8dcc4" stop-opacity="0.95" />
          <stop offset="100%" stop-color="#c9b79c" stop-opacity="0.88" />
        </radialGradient>
      </defs>
      <rect width="900" height="600" fill="url(#bg)" />
      <circle cx="450" cy="300" r="210" fill="url(#retina)" stroke="#fff" stroke-opacity="0.18" stroke-width="6" />
      <circle cx="520" cy="260" r="52" fill="${accent}" fill-opacity="0.85" />
      <circle cx="520" cy="260" r="18" fill="#09111f" fill-opacity="0.7" />
      <path d="M275 220 C350 170, 470 150, 620 200" stroke="${accent}" stroke-width="16" stroke-linecap="round" stroke-opacity="0.35" fill="none" />
      <path d="M270 320 C360 360, 480 390, 640 360" stroke="${accent}" stroke-width="14" stroke-linecap="round" stroke-opacity="0.28" fill="none" />
      <path d="M320 430 C410 360, 530 330, 620 250" stroke="${accent}" stroke-width="12" stroke-linecap="round" stroke-opacity="0.24" fill="none" />
      <text x="450" y="515" text-anchor="middle" fill="#ffffff" font-family="Arial, sans-serif" font-size="30" font-weight="700">${title}</text>
    </svg>
  `;
  return `data:image/svg+xml;base64,${toBase64(svg)}`;
};

export const getDemoProviders = (city) => {
  const normalized = (city || '').trim().toLowerCase();
  if (!normalized) return demoProviders;
  return demoProviders.filter((provider) => provider.city.toLowerCase().includes(normalized));
};

export const getDemoMetrics = () => demoMetrics;

export const getDemoDashboard = () => demoDashboard;

export const getDemoPatients = () => demoPatients;

export const getDemoHistory = (id) => demoHistory[id] || [];

export const buildDemoAnalysis = ({ file, patientId, mode }) => {
  const fileSize = file?.size || 0;
  const severitySeed = Math.min(95, Math.max(12, Math.round((fileSize % 700000) / 8000) + (mode === 'combined' ? 18 : 10)));
  const confidence = Math.min(0.98, Math.max(0.55, 0.55 + severitySeed / 220));
  const glaucomaRisk = mode !== 'dr' && severitySeed > 55;

  return {
    id: Date.now(),
    patient_id: patientId || null,
    mode: mode || 'combined',
    preview: '',
    confidence,
    risk_score: severitySeed,
    cdr: Number((0.18 + severitySeed / 250).toFixed(2)),
    dr_grade: severitySeed > 78 ? 3 : severitySeed > 58 ? 2 : severitySeed > 35 ? 1 : 0,
    dr_stage_label: severitySeed > 78 ? 'Severe DR' : severitySeed > 58 ? 'Moderate DR' : severitySeed > 35 ? 'Mild DR' : 'No apparent DR',
    glaucoma: glaucomaRisk ? 1 : 0,
    glaucoma_label: glaucomaRisk ? 'Glaucoma suspect' : 'Low glaucoma risk',
    primary_diagnosis: glaucomaRisk
      ? 'Retinal image suggests glaucoma suspicion with diabetic retinopathy changes.'
      : severitySeed > 35
        ? 'Retinal image suggests diabetic retinopathy changes requiring specialist follow-up.'
        : 'No major diabetic retinopathy signs detected in this scan.',
    patient_summary: glaucomaRisk
      ? 'The scan shows retinal changes that deserve a glaucoma and retina review.'
      : severitySeed > 35
        ? 'The scan suggests diabetic retinopathy changes. Control blood sugar and arrange follow-up.'
        : 'The scan does not show major retinal disease, but routine monitoring is still important.',
    disease_predictions: [
      {
        disease: 'Diabetic Retinopathy',
        status: severitySeed > 35 ? 'Detected' : 'Not detected',
        severity: severitySeed > 78 ? 'High' : severitySeed > 58 ? 'Moderate' : severitySeed > 35 ? 'Mild' : 'Low',
        confidence_percent: Math.round(confidence * 100)
      },
      {
        disease: 'Glaucoma',
        status: glaucomaRisk ? 'Suspected' : 'Low risk',
        severity: glaucomaRisk ? 'Moderate' : 'Low',
        confidence_percent: Math.round((glaucomaRisk ? confidence - 0.08 : confidence - 0.18) * 100)
      }
    ],
    treatment_suggestions: glaucomaRisk
      ? [
          'Book a glaucoma specialist appointment within 7 days.',
          'Ask for intraocular pressure and optic nerve evaluation.',
          'Keep blood pressure and blood sugar tightly controlled.',
          'Avoid self-starting eye drops without a doctor review.'
        ]
      : [
          'Book a retinal eye examination with dilation.',
          'Maintain strict blood sugar control and routine HbA1c follow-up.',
          'Use the provider list below to schedule specialist review.',
          'Repeat imaging as advised by your ophthalmologist.'
        ],
    suggested_providers: getDemoProviders(),
    next_steps: [
      'Review the result with a qualified eye specialist.',
      'Share the scan summary with your primary physician.',
      'Track blood sugar, blood pressure, and follow-up visits.'
    ],
    recommendations: [
      'This self-contained build uses demo clinical logic when the backend is not deployed.',
      'Treat the output as decision support, not a final medical diagnosis.'
    ],
    scan_details: {
      analyzed_region: 'Retinal fundus',
      scanned_area_percent: 92,
      optic_disc_center: [128, 128],
      optic_disc_radius: 48,
      vessel_density_percent: 31,
      quality_checks: {
        blur_score: 0.82,
        brightness_score: 0.76,
        retinal_detected: true
      },
      limitations: [
        'Demo mode is used when the API backend is unavailable.',
        'The displayed findings are deterministic placeholders for redeployment testing.'
      ]
    },
    gradcam_base64: makeOverlay('Demo Grad-CAM Overlay', '#fca311'),
    lesion_base64: makeOverlay('Demo Lesion Mask', '#2a9d8f'),
    optic_disc_base64: makeOverlay('Demo Optic Disc View', '#e76f51')
  };
};
