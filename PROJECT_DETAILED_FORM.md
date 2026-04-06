# RetinalAI Detailed Project Form (Presentation Ready)

## 1. Project Title
RetinalAI - Automated Eye Disease Diagnosis System

## 2. Problem Statement
Manual retinal screening is time-consuming and specialist-dependent. Many patients do not get early diabetic retinopathy or glaucoma screening due to accessibility gaps.

## 3. Solution Overview
RetinalAI is a full-stack AI-assisted platform that:
- Accepts retinal fundus images
- Validates that uploaded image is actually an eye fundus image
- Performs AI-based risk estimation for diabetic retinopathy and glaucoma indicators
- Generates explainability overlays
- Provides patient-friendly summary and next steps
- Stores patient and scan history for follow-up
- Generates PDF clinical report

## 4. Core Clinical Tasks Covered
- Diabetic Retinopathy risk grading (0-4 scale)
- Glaucoma risk (binary risk signal)
- Cup-to-Disc Ratio estimation (CDR)
- Risk score generation (0-100)
- Explainability visualization (heatmap, lesion overlay, optic-disc crop)

## 5. End-to-End Architecture
### Frontend
- React 18 + Vite
- TailwindCSS
- Recharts for data visualizations
- Axios for API communication

### Backend
- FastAPI for REST APIs
- SQLAlchemy ORM for data layer
- SQLite (local simplified run) and PostgreSQL-ready config
- OpenCV + NumPy for image processing
- ReportLab for PDF report generation

### ML Layer
- Dataset unification pipeline
- MESSIDOR2-focused training pipeline
- Traditional ML classifier (RandomForest) for current stable local training path
- PyTorch model scaffolding for advanced deep learning path

## 6. Tools and Libraries Used (Feature-Wise)
### A. Frontend Features and Tools
1. Routing and multi-page app:
- react-router-dom

2. API integration:
- axios

3. UI system and responsive design:
- tailwindcss, postcss, autoprefixer

4. Charts and analytics dashboards:
- recharts

5. Icons and visual cues:
- lucide-react

6. Build/dev server:
- vite, @vitejs/plugin-react

### B. Backend Features and Tools
1. API framework:
- fastapi
- uvicorn

2. File upload handling:
- python-multipart

3. Data models and persistence:
- sqlalchemy
- alembic
- psycopg (PostgreSQL driver, deployment mode)
- sqlite (default local mode)

4. Config and environment:
- pydantic
- pydantic-settings

5. Image quality and retinal validation:
- opencv-python-headless
- numpy

6. Report generation:
- reportlab

7. Utility/time/http support:
- python-dateutil
- httpx

### C. ML/Data Features and Tools
1. Dataset processing:
- pandas
- tqdm

2. CV preprocessing and enhancement:
- opencv-python-headless
- albumentations
- numpy

3. Training and model support:
- scikit-learn (active MESSIDOR2 trainer path)
- torch, torchvision (advanced model path)

4. Evaluation and analysis:
- scikit-learn metrics
- matplotlib
- seaborn

5. Config-driven training:
- pyyaml

## 7. Data Sources Supported in Project
- DIARETDB1
- APTOS 2019
- MESSIDOR2
- ORIGA
- DRIVE
- RFMiD

Current practical training path optimized for:
- MESSIDOR2

## 8. Data Engineering Pipeline
1. Ingest images from dataset folders
2. Parse labels (CSV/TSV/XLSX supported for key datasets)
3. Normalize target schema:
- dr_grade
- glaucoma
- cdr
4. Build master dataset table:
- data/metadata/master_dataset.csv
5. Patient-level split
6. Corrupt image filtering

## 9. Image Preprocessing and Validation Pipeline
1. Retinal-only acceptance checks:
- Brightness check
- Blur check
- Circular/fundus shape checks
- Texture/edge checks

2. Enhancement steps:
- Circular crop / fundus mask extraction
- Ben Graham enhancement
- CLAHE-based enhancement
- Gaussian background subtraction
- Vessel enhancement map
- Optic disc detection and crop
- CDR estimate

3. Overlay generation:
- Grad-CAM-like heatmap (masked to retinal region)
- Lesion color overlay (masked to retinal region)

## 10. Inference/Prediction Strategy (Current)
1. If trained MESSIDOR2 model exists:
- Backend loads ml/models/weights/messidor2_rf.joblib
- Uses extracted retinal features for DR-grade prediction

2. Fallback mode:
- Heuristic signal fusion for stable operation without model file

3. Additional outputs:
- Risk score
- Confidence
- Uncertainty (mean/std)
- Patient summary and next steps

## 11. Backend API Endpoints
- POST /api/analyze
- GET /api/patients
- POST /api/patients
- GET /api/patients/{id}/history
- POST /api/report/generate
- GET /api/model/metrics
- GET /api/dashboard/stats
- GET /health

## 12. Database Entities
- Patients
- Scans
- Reports
- ModelVersions

## 13. Key User Flows
### Flow 1: Upload and Analyze
1. User selects retinal eye image
2. Backend validates image is retinal/fundus
3. System preprocesses image and runs inference
4. Results shown with overlays and plain-language summary

### Flow 2: Patient Tracking
1. Add patient profile
2. Analyze image with selected patient
3. Scan gets attached to patient history
4. Trend and progression available in patient section

### Flow 3: Report Generation
1. Use scan ID
2. Generate PDF with image + heatmap + findings + recommendations

## 14. Explainability and Transparency Features
- Overlay toggle (Grad-CAM / Lesion / Optic Disc)
- Scan details report:
  - What region was scanned
  - Scanned area percent
  - Quality metrics
  - Optic disc location
  - Vessel density
  - Limitations and caution notes

## 15. Dashboard/Graph Features
- Scan activity timeline
- Disease distribution chart
- Risk band chart
- Performance curves (ROC/PR/Calibration placeholders)

## 16. Local Run (No Docker, Simplified)
Primary script:
- run_local.ps1

What it does:
1. Installs backend deps
2. Installs frontend deps
3. Starts backend server
4. Starts frontend server

## 17. Training Command (MESSIDOR2)
python -m ml.training.train_messidor2

Outputs:
- Trained model: ml/models/weights/messidor2_rf.joblib
- Metrics CSV: reports/generated/messidor2_training_metrics.csv

## 18. Production/Deployment Readiness Notes
Implemented:
- Full stack structure
- CI workflow
- Docker compose and NGINX configs (optional)
- Local no-Docker path for simplicity

Recommended before live rollout:
1. Increase clinical validation dataset size
2. Improve model metrics to target threshold
3. Add independent medical validation and QA
4. Add audit logging and model monitoring
5. Run pilot with clinician feedback loop

## 19. Interview/Presentation Talking Points
1. Why this project:
- Early eye disease detection accessibility

2. What makes it practical:
- Patient-friendly outputs + explainability + history tracking

3. Technical strengths:
- Modular ML/backend/frontend architecture
- Dataset normalization across multiple public retinal datasets
- Local-first run for easy demonstration

4. Real-world constraints acknowledged:
- AI decision support, not autonomous diagnosis
- Quality and validation constraints explicitly shown to user

## 20. Current Status Summary
- Project runs locally without Docker complexity
- MESSIDOR2 training pipeline implemented and executed
- Retinal-only input validation implemented
- Detailed scan explanation added for user transparency
- Patient workflow and report generation available
