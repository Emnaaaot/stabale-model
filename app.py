import requests

response = requests.post(
    "https://api.stability.ai/v2beta/stable-image/generate/ultra",
    headers={
        "Authorization": "Bearer sk-",
        "Accept": "image/*"  # Correct the Accept header here
    },
    files={
        "prompt": (None, "Lighthouse on a cliff overlooking the ocean"),
        "output_format": (None, "webp")
    },
)

if response.status_code == 200:
    with open("./lighthouse.webp", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(f"Error: {response.status_code}, Message: {response.text}")
