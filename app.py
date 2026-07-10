"""
VitalSense AI - Flask Application
Disease Prediction API using pre-trained RandomForest model.
"""

import os
import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ── Load model bundle once at startup ──────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "disease_model.pkl")
bundle = joblib.load(MODEL_PATH)

model = bundle["model"]
scaler = bundle["scaler"]
label_encoder = bundle["label_encoder"]
gender_encoder = bundle["gender_encoder"]
feature_cols = bundle["feature_cols"]
numeric_cols = bundle["numeric_cols"]

# Symptom list (must match training order)
SYMPTOMS = [
    "fever", "cough", "headache", "sore_throat", "fatigue", "chest_pain",
    "vomiting", "diarrhea", "nausea", "body_pain", "chills", "runny_nose",
    "shortness_of_breath", "joint_pain", "skin_rash", "abdominal_pain",
    "dizziness", "loss_of_smell", "loss_of_taste", "sweating", "anxiety",
    "depression", "back_pain", "ear_pain", "eye_pain", "swollen_glands",
    "frequent_urination", "weight_loss", "constipation", "muscle_weakness"
]

DISEASE_DESCRIPTIONS = {
    "Common Cold": "A viral infection of the upper respiratory tract. Usually harmless and resolves within a week.",
    "Flu": "Influenza - a contagious respiratory illness caused by influenza viruses. Can cause mild to severe illness.",
    "COVID-19": "A respiratory illness caused by the SARS-CoV-2 virus. Symptoms range from mild to severe.",
    "Malaria": "A mosquito-borne disease caused by Plasmodium parasites. Requires immediate medical attention.",
    "Dengue": "A mosquito-borne viral infection causing flu-like illness. Can develop into severe dengue.",
    "Diabetes": "A chronic condition affecting how the body processes blood sugar (glucose).",
    "Hypertension": "High blood pressure - a common condition where blood flows through arteries at higher than normal pressures.",
    "Asthma": "A condition in which airways narrow and swell, producing extra mucus and causing breathing difficulty.",
    "Pneumonia": "Infection that inflames air sacs in one or both lungs, which may fill with fluid.",
    "Food Poisoning": "An illness caused by eating contaminated food. Usually resolves within a few days.",
    "Migraine": "A headache of varying intensity, often accompanied by nausea and sensitivity to light and sound.",
    "Typhoid": "A bacterial infection that can spread throughout the body, affecting many organs.",
    "Tuberculosis": "A potentially serious infectious bacterial disease that mainly affects the lungs.",
    "Allergies": "An immune system reaction to a foreign substance that's not typically harmful.",
    "Viral Fever": "A fever caused by a viral infection. Symptoms include elevated body temperature, headache, and body aches."
}

DISEASE_ADVICE = {
    "Common Cold": "Rest, stay hydrated, and use over-the-counter cold medications. Consult a doctor if symptoms persist beyond 10 days.",
    "Flu": "Get plenty of rest, drink fluids, and take antiviral medications if prescribed. Seek care if symptoms worsen.",
    "COVID-19": "Isolate yourself, monitor oxygen levels, and seek medical attention immediately if breathing becomes difficult.",
    "Malaria": "Seek immediate medical care. Treatment with antimalarial drugs is essential.",
    "Dengue": "Stay hydrated, rest, and monitor for warning signs. Seek hospital care if symptoms worsen.",
    "Diabetes": "Monitor blood sugar regularly, follow a balanced diet, exercise, and take prescribed medications.",
    "Hypertension": "Reduce salt intake, exercise regularly, manage stress, and take prescribed blood pressure medications.",
    "Asthma": "Use inhalers as prescribed, avoid triggers, and seek emergency care if breathing becomes severely difficult.",
    "Pneumonia": "Seek medical attention promptly. Treatment may include antibiotics (for bacterial) or antivirals.",
    "Food Poisoning": "Stay hydrated with oral rehydration solutions. Seek care if symptoms are severe or persist.",
    "Migraine": "Rest in a dark, quiet room. Use prescribed medications and identify/avoid triggers.",
    "Typhoid": "Seek medical care immediately. Antibiotic therapy and proper hydration are essential.",
    "Tuberculosis": "Requires long-term antibiotic treatment under medical supervision. Isolate to prevent spread.",
    "Allergies": "Avoid known allergens, use antihistamines, and consider allergy shots for severe cases.",
    "Viral Fever": "Rest, stay hydrated, and take fever-reducing medications. Consult a doctor if fever persists."
}


# ── Routes ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", symptoms=SYMPTOMS)


@app.route("/predict", methods=["POST"])
def predict():
    """API endpoint for disease prediction."""
    try:
        data = request.get_json()

        # Build patient dict from request
        patient = {
            "age": float(data.get("age", 0)),
            "gender": data.get("gender", "Male"),
            "weight_kg": float(data.get("weight_kg", 0)),
            "height_cm": float(data.get("height_cm", 0)),
            "body_temp_f": float(data.get("body_temp_f", 0)),
            "bp_systolic": float(data.get("bp_systolic", 0)),
            "bp_diastolic": float(data.get("bp_diastolic", 0)),
            "heart_rate": float(data.get("heart_rate", 0)),
            "blood_sugar": float(data.get("blood_sugar", 0)),
            "oxygen_level": float(data.get("oxygen_level", 0)),
        }

        # Add symptoms (default to 0 if not provided)
        for symptom in SYMPTOMS:
            patient[symptom] = 1 if data.get(symptom, False) else 0

        # Run prediction
        result = predict_one(patient)
        return jsonify({"success": True, **result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── Prediction helper ──────────────────────────────────────────────

def predict_one(patient: dict):
    """Run ML prediction on a single patient record."""
    row = {s: patient.get(s, 0) for s in SYMPTOMS}
    row.update({
        "age": patient["age"],
        "weight_kg": patient["weight_kg"],
        "height_cm": patient["height_cm"],
        "body_temp_f": patient["body_temp_f"],
        "bp_systolic": patient["bp_systolic"],
        "bp_diastolic": patient["bp_diastolic"],
        "heart_rate": patient["heart_rate"],
        "blood_sugar": patient["blood_sugar"],
        "oxygen_level": patient["oxygen_level"],
        "gender_enc": gender_encoder.transform([patient["gender"]])[0],
    })

    X = pd.DataFrame([row])[feature_cols]
    X[numeric_cols] = scaler.transform(X[numeric_cols])

    pred_idx = model.predict(X)[0]
    proba = model.predict_proba(X)[0]

    disease = label_encoder.inverse_transform([pred_idx])[0]
    confidence = round(float(proba[pred_idx]) * 100, 1)

    # Top 3 ranked diseases
    ranked = sorted(
        zip(label_encoder.classes_, proba), key=lambda x: x[1], reverse=True
    )[:3]
    ranked = [{"disease": name, "confidence": round(float(p) * 100, 1)} for name, p in ranked]

    return {
        "predicted_disease": disease,
        "confidence_pct": confidence,
        "top3": ranked,
        "description": DISEASE_DESCRIPTIONS.get(disease, ""),
        "advice": DISEASE_ADVICE.get(disease, ""),
    }


# ── Error handlers ─────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Internal server error"}), 500


# ── Entry point ────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
