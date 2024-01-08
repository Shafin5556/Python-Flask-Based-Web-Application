import requests

CHUNK_SIZE = 1024
url = "https://api.elevenlabs.io/v1/text-to-speech/DyCTAyMqJLVo64stQETq"

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": "980c63b1108ebae8554d39d5591fad14"
}

data = {
    "text": "Hi! My name is Bella, nice to meet you!",
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.9,
        "similarity_boost": 0.9
    }
}

response = requests.post(url, json=data, headers=headers)
with open('output.mp3', 'wb') as f:
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            f.write(chunk)
