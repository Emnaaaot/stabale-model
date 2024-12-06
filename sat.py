import os
import time
from flask import Flask, request, jsonify

import requests

# Load environment variables from .env file


app = Flask(__name__)
os.makedirs("static", exist_ok=True)

# Environment variables and configuration
STABLE_AI_API_KEY = "sk-HZiNPQvTfwh68RsYEE1kUeeH6TRth7Sn5npEwDgPKXlYoFUY"  # API key for Stable AI (for image generation)
GEMINI_API_KEY = "AIzaSyB5nVROnrxWN75vLY4N2GFNwXRJ8_TdKXE" # API key for Gemini API (your generative AI key)

# Function to fetch response from Gemini API
def get_gemini_response(question):
    """Fetches the response from Gemini API."""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
    }
    payload = {
        "contents": [
            {"parts": [{"text": question}]}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises HTTPError if the response was an error
        return response.json().get("contents", [{}])[0].get("parts", [{}])[0].get("text", "No response available.")
    except Exception as e:
        return f"Error during Gemini API request: {str(e)}"


    def add_diagnosis(self, diagnosis):
        self.set_font('Arial', '', 10)
        self.ln(10)
        for key, value in diagnosis.items():
            self.cell(0, 10, f"{key}: {value}", ln=True)

# Diagnose endpoint
@app.route('/diagnose', methods=['POST'])
def diagnose():
    """Analyze ocean symptoms provided as free-text input."""
    description = request.json.get("description", "").strip()

    if not description:
        return jsonify({"error": "Veuillez fournir une description des symptômes environnementaux."}), 400

    # Define keywords for symptom detection
    keywords = {
        "temperature": ["chaud", "température élevée", "réchauffement"],
        "pollution": ["plastique", "déchets", "pollution", "chimique"],
        "biodiversity": ["biodiversité", "espèces", "faune"],
        "dying_fishes": ["poissons morts", "mort", "faim"],
        "water_color": ["eau colorée", "eau sale", "teintée"],
        "coral_health": ["coraux", "blanchiment", "détruits"]
    }

    # Detect symptoms based on keywords
    detected_symptoms = {}
    for symptom, terms in keywords.items():
        if any(term in description.lower() for term in terms):
            detected_symptoms[symptom] = f"Symptôme détecté : lié à {symptom}"

    if not detected_symptoms:
        return jsonify({"error": "Aucun symptôme pertinent détecté dans la description."}), 400

    # # Generate recommendations using Gemini API
    # ai_recommendations = get_gemini_response(f"Provide recommendations for ocean symptoms: {description}")

    # Stable Diffusion API for "good" and "bad" ocean images
    headers = {
        "Authorization": f"Bearer {STABLE_AI_API_KEY}",
        "Accept": "image/*"
    }
    images = {}
    image_prompts = {
        "positive": "A clean ocean with vibrant coral reefs, healthy marine life, and clear blue water.",
        "negative": "A polluted ocean with dead fishes, trash floating, and dark, murky water."
    }
    for state, prompt in image_prompts.items():
        try:
            response = requests.post(
                "https://api.stability.ai/v2beta/stable-image/generate/ultra",
                headers=headers,
                files={
                    "prompt": (None, prompt),
                    "output_format": (None, "webp"),
                    "cfg_scale": (None, "7"),
                    "height": (None, "512"),
                    "width": (None, "512"),
                    "samples": (None, "1"),
                }
            )
            if response.status_code == 200:
                image_path = os.path.join("static", f"{state}_image_{int(time.time())}.webp")
                with open(image_path, "wb") as f:
                    f.write(response.content)
                images[state] = f"/static/{os.path.basename(image_path)}"
            else:
                images[state] = f"Failed to generate {state} image: {response.text}"
        except Exception as e:
            images[state] = f"Error generating {state} image: {str(e)}"

    # Generate PDF report
    pdf = OceanReport()
    pdf.add_page()
    pdf.add_diagnosis(detected_symptoms)
    report_path = os.path.join("static", "ocean_report.pdf")
    pdf.output(report_path)

    return jsonify({
        "diagnosis": detected_symptoms,
        "recommendations": ai_recommendations,
        "images": images,
        "report_url": report_path
    })

# Ask endpoint
@app.route('/ask', methods=['POST'])
def ask():
    """Handle user questions about ocean health."""
    question = request.json.get("question", "").strip()

    if not question:
        return jsonify({"error": "Veuillez fournir une question."}), 400

    ocean_keywords = [
        "océan", "pollution", "coraux", "biodiversité", "poissons", "climat", "protection", "réchauffement", "acidification"
    ]
    if not any(keyword in question.lower() for keyword in ocean_keywords):
        return jsonify({
            "response": (
                "Je suis un médecin pour l'océan, et je me concentre sur ses problèmes de santé. "
                "Malheureusement, je ne suis pas expert en ce domaine. "
                "Avez-vous une question sur l’état de santé de l’océan ou des moyens de le protéger ?"
            )
        })

    ai_response = get_gemini_response(question)
    return jsonify({"response": ai_response})

# Run Flask application
if __name__ == '__main__':
    app.run(debug=True)
