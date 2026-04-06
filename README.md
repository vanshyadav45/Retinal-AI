# RetinalAI - Automated Eye Disease Diagnosis System

RetinalAI is a full-stack AI platform for retinal fundus image analysis focused on:

- Diabetic Retinopathy 5-class grading
- Glaucoma binary detection + CDR estimation
- Explainability overlays and uncertainty estimation
- Clinical PDF report generation

## Project Structure

- frontend: React + Tailwind clinical UI
- backend: FastAPI inference and data services
- ml: Training, evaluation, explainability, and ensemble calibration
- data: Raw and processed data plus metadata
- reports: Generated PDF outputs
- notebooks: Experiment notebooks
- nginx: Reverse proxy config

## Features Implemented

- Unified dataset builder for DIARETDB1, APTOS2019, MESSIDOR2, ORIGA, DRIVE, RFMiD
- Normalized labels: dr_grade, glaucoma, cdr in master_dataset.csv
- Patient-level split and corrupt image filtering
- Preprocessing pipeline: CLAHE, green channel, Ben Graham, circular crop, Gaussian subtraction, resize, normalization
- Vessel enhancement, optic disc detection/crop, CDR estimate
- DR classifier and glaucoma model definitions in PyTorch
- Optional lesion segmentation model scaffold (U-Net style)
- Mixed precision training, cosine restarts, gradient clipping, early stopping
- Ensemble weighting and temperature scaling
- Explainability modules: Grad-CAM, EigenCAM, LIME/SHAP stubs
- FastAPI endpoints for analysis, patients, reports, metrics, dashboard
- PostgreSQL persistence with SQLAlchemy ORM
- PDF generation using ReportLab
- Dockerized services + NGINX reverse proxy + MLflow tracking
- GitHub Actions CI for frontend/backend/ml checks

## API Endpoints

- POST /api/analyze
- GET /api/patients
- POST /api/patients
- GET /api/patients/{id}/history
- POST /api/report/generate
- GET /api/model/metrics
- GET /api/dashboard/stats

## Quick Start

1. Copy environment values if needed:
   - root .env.example
   - backend/.env.example
2. Start stack:

```bash
docker compose up --build
```

3. Open applications:

- Frontend via NGINX: http://localhost
- Direct frontend container: http://localhost:5173
- Backend API docs: http://localhost:8000/docs
- MLflow: http://localhost:5000

## Run Locally Without Docker (Recommended)

```bash
./run_local.ps1
```

This starts backend and frontend in separate terminals.

## Train With MESSIDOR2

1. Put MESSIDOR2 images under `data/raw/MESSIDOR2`.
2. Add labels file in that folder (`labels.csv` or `labels.xlsx`) with image and grade columns.
3. Run:

```bash
python -m ml.training.train_messidor2
```

The trained model is saved to `ml/models/weights/messidor2_rf.joblib` and is used automatically by backend inference.

## Model Training

Install ML dependencies and run:

```bash
pip install -r ml/requirements.txt
python -m ml.training.train
python -m ml.training.train_glaucoma
```

## Dataset Setup

Dataset folders are pre-created:

- data/raw/DIARETDB1
- data/raw/APTOS2019
- data/raw/MESSIDOR2
- data/raw/ORIGA
- data/raw/DRIVE
- data/raw/RFMiD

Use the helper script to fetch what is automatable and print manual instructions for gated datasets:

```bash
python -m ml.data.fetch_datasets --dataset all
```

### DIARETDB1 quick training format

If you downloaded DIARETDB1 manually, place files under [data/raw/DIARETDB1](data/raw/DIARETDB1) and add [data/raw/DIARETDB1/labels.csv](data/raw/DIARETDB1/labels.csv) with columns:

- image
- dr_grade
- glaucoma (optional)
- cdr (optional)
- patient_id (optional)

Example row:

```csv
image,dr_grade,glaucoma,cdr,patient_id
images/IMG_001.png,2,0,0.48,P001
```

Then run:

```bash
python -m ml.training.train_diaretdb1
```

## AWS EC2 + SSL Deployment Notes

- Use GPU AMI (for model training/inference acceleration)
- Run Docker Engine + Compose plugin
- Expose 80/443 and configure domain DNS to EC2 IP
- Issue certificates with certbot and mount into NGINX
- Add HTTPS server block in nginx/default.conf for production

## Notes

- This repository intentionally excludes authentication per requirements.
- Explainability LIME/SHAP components are scaffolded with lightweight stubs that can be replaced with full integrations for production scale.
