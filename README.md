# VitalSense AI - Flask Web App

A full-stack Flask application for AI-powered disease prediction using a pre-trained RandomForest model. Deploy-ready for [Render](https://render.com/).


## Live Demo:
https://disease-prediction-fnvu.onrender.com

## Features

- **Beautiful, responsive UI** - Modern medical-themed interface
- **Real-time predictions** - 15 disease classes with confidence scores
- **ML-powered backend** - RandomForest classifier (~90% accuracy)
- **Top-3 results** - Ranked predictions with confidence bars
- **Medical advice** - Personalized recommendations per disease
- **Render-ready** - One-click deployment configuration

## Project Structure

```
vitalsense-app/
├── app.py                  # Flask app with /predict API
├── wsgi.py                 # WSGI entry point
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment config
├── disease_model.pkl       # Pre-trained ML model
├── training_metrics.json   # Model performance metrics
├── templates/
│   └── index.html          # Frontend UI
└── static/
    ├── css/
    │   └── style.css       # App styling
    └── js/
        └── app.js          # Frontend logic
```

## Quick Start (Local)

```bash
# 1. Navigate to project
cd vitalsense-app

# 2. Create virtual environment
python -m venv venv

# 3. Activate (macOS/Linux)
source venv/bin/activate
#    Activate (Windows)
#    venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the app
python app.py

# 6. Open browser → http://localhost:5000
```

## Deploy to Render

### Option 1: Using render.yaml (Blueprint)

1. Push this repo to GitHub
2. In Render dashboard, click **New +** → **Blueprint**
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml` and deploy

### Option 2: Manual Web Service

1. Push this repo to GitHub
2. In Render dashboard, click **New +** → **Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
5. Click **Create Web Service**

## API Endpoint

### `POST /predict`

Predict disease from patient vitals and symptoms.

**Request Body (JSON):**
```json
{
  "age": 34,
  "gender": "Male",
  "weight_kg": 72.5,
  "height_cm": 175.2,
  "body_temp_f": 102.4,
  "bp_systolic": 120,
  "bp_diastolic": 80,
  "heart_rate": 85,
  "blood_sugar": 100,
  "oxygen_level": 98,
  "fever": true,
  "cough": false,
  "headache": true
}
```

**Response:**
```json
{
  "success": true,
  "predicted_disease": "Flu",
  "confidence_pct": 87.5,
  "top3": [
    {"disease": "Flu", "confidence": 87.5},
    {"disease": "Viral Fever", "confidence": 8.2},
    {"disease": "COVID-19", "confidence": 2.1}
  ],
  "description": "Influenza - a contagious respiratory illness...",
  "advice": "Get plenty of rest, drink fluids..."
}
```

## Model Performance

| Metric | Value |
|--------|-------|
| Test Accuracy | 90.38% |
| Weighted F1 | 90.30% |
| CV Accuracy | 91.03% |
| Classes | 15 diseases |

## 15 Predictable Diseases

Allergies, Asthma, COVID-19, Common Cold, Dengue, Diabetes, Flu, Food Poisoning, Hypertension, Malaria, Migraine, Pneumonia, Tuberculosis, Typhoid, Viral Fever

## Important Disclaimer

This tool is for **educational and demonstration purposes only**. The model is trained on synthetic data and is **not a certified diagnostic tool**. Always consult a qualified healthcare professional for medical advice, diagnosis, or treatment.

## License

MIT License - Feel free to use and modify.
