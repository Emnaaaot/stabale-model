from flask import Flask, render_template, request, url_for, jsonify
import requests
import os
import time
import base64

app = Flask(__name__)

# Initialize variables
image_history = []
API_KEY = 'your_api_key_here'

@app.route('/', methods=['GET', 'POST'])
def index():
    global image_history
    new_image_url = None

    if request.method == "POST":
        prompt = request.form.get("prompt")

        try:
            # Updated API call with JSON payload
            response = requests.post(
                "https://api.stability.ai/v2beta/stable-image/generate/ultra",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json={
                    "prompt": prompt,
                    "output_format": "webp",
                    "seed": 0,  # Optional: for reproducibility
                    "style_preset": "photographic"  # Optional: can be adjusted
                }
            )

            # Check for successful response
            if response.status_code == 200:
                # Parse the JSON response
                response_data = response.json()

                # Decode the base64 image
                image_base64 = response_data['image']

                # Use timestamp for a unique filename
                image_name = f"generated_image_{int(time.time())}.webp"
                image_path = os.path.join("static", image_name)

                # Decode and save the image
                image_bytes = base64.b64decode(image_base64)
                with open(image_path, 'wb') as file:
                    file.write(image_bytes)

                # Generate URL for the saved image
                new_image_url = url_for('static', filename=image_name)

                # Add the new image to the history
                image_history.append(new_image_url)
            else:
                # Handle API errors
                return jsonify({
                    "error": f"API Error: {response.status_code}",
                    "message": response.text
                }), 400

        except requests.exceptions.RequestException as e:
            # Handle network-related errors
            return jsonify({
                "error": "Network Error",
                "message": str(e)
            }), 500
        except Exception as e:
            # Handle other unexpected errors
            return jsonify({
                "error": "Unexpected Error",
                "message": str(e)
            }), 500

    return render_template("index.html", new_image_url=new_image_url, image_history=image_history)

if __name__ == "__main__":
    # Ensure the static directory exists
    os.makedirs("static", exist_ok=True)
    app.run(debug=True)
