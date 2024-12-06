from flask import Flask, request, jsonify
from gpt4all import GPT4All

app = Flask(_name_)
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        user_prompt = data['prompt']

        # Add specific context to focus on book-related questions
        prompt = f" recommended marine vehicles that are environmentally friendly and do not produce CO₂ emissions,   {user_prompt}"

        response = model.generate(prompt)
        return jsonify({'response': response})
    except Exception as e:
        # Log error for debugging
        app.logger.error(f"Exception: {e}")
        # Return error response
        return jsonify({'error': 'An error occurred during processing.'}), 500

if _name_ == '_main_':
    app.run(host="0.0.0.0",port=5000, debug=True)