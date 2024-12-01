from flask import Flask, render_template, request, url_for
import requests
import os
import time

app = Flask(__name__)

API_KEY = ""

# Store generated images in a list for history
image_history = []

@app.route("/", methods=["GET", "POST"])
def index():
    global image_history
    new_image_url = None
    if request.method == "POST":
        prompt = request.form.get("prompt")
        response = requests.post(
            "https://api.stability.ai/v2beta/stable-image/generate/ultra",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Accept": "image/*"
            },
            files={
                "prompt": (None, prompt),
                "output_format": (None, "webp")
            },
        )

        if response.status_code == 200:
            # Use timestamp for a unique filename
            image_name = f"generated_image_{int(time.time())}.webp"
            image_path = os.path.join("static", image_name)
            with open(image_path, 'wb') as file:
                file.write(response.content)

            new_image_url = url_for('static', filename=image_name)
            # Add the new image to the history
            image_history.append(new_image_url)
        else:
            return f"Error: {response.status_code}, Message: {response.text}"

    return render_template("index.html", new_image_url=new_image_url, image_history=image_history)

if __name__ == "__main__":
    app.run(debug=True)
