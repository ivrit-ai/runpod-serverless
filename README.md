# runpod-serverless

[![RunPod](https://api.runpod.io/badge/ivrit-ai/runpod-serverless)](https://www.runpod.io/console/hub/ivrit-ai/runpod-serverless)

A template for quickly deploying an ivrit.ai Speech-to-text API.

Note: if you register at [runpod.io](https://runpod.io), we'd like to ask you to consider using our [referral link](https://runpod.io/?ref=06octndf).
It provides us with credits, which we can then use to provide better services.

## Description

This project provides a serverless solution for transcribing Hebrew audio files. It leverages runpod.io's infrastructure to process audio files efficiently and return transcriptions.
It is part of the [ivrit.ai](https://ivrit.ai) non-profit project.

## API: easy deployment through the Runpod hub

If you simply want to use our models via an API, quick deploy is avaialble via the RunPod hub.

1. Open this template on the hub by clicking [here](https://www.runpod.io/console/hub/ivrit-ai/runpod-serverless).
2. Click the "Deploy" button and create the endpoint.
3. Follow the instructions under the [Usage](#usage) section.

## Contents

- `Dockerfile`: Used to create the Docker image for the serverless function.
- `infer.py`: The main script that handles the transcription process, placed inside the Docker image.

## Setting up your inference endpoint

1. Log in to [runpod.io]
2. Choose Menu->Serverless
3. Choose New Endpoint
4. Select the desired worker configuration.
   - You can choose the cheapest worker (16GB GPU, $0.00016/second as of August 1st, 2024).
   - Active workers can be 0, max workers is 1 or more.
   - GPUs/worker should be set to 1.
   - Container image should be set to **yairlifshitz/whisper-runpod-serverless:latest**, or your own Docker image (instruction later on how to build this).
   - Container disk should have at least 20 GB.
5. Click Deploy.

## Building your own Docker image

1. Clone this repository:

```
git clone https://github.com/ivrit-ai/runpod-serverless.git
cd runpod-serverless
```

2. Build the Docker image:

```
docker build -t whisper-runpod-serverless .
```

3. Push the image to a public Docker repository:

a. If you haven't already, create an account on [Docker Hub](https://hub.docker.com/).

b. Log in to Docker Hub from your command line:
   ```
   docker login
   ```

c. Tag your image with your Docker Hub username:
   ```
   docker tag whisper-runpod-serverless yourusername/whisper-runpod-serverless:latest
   ```

d. Push the image to Docker Hub:
   ```
   docker push yourusername/whisper-runpod-serverless:latest
   ```

4. Set up a serverless function on runpod.io using the pushed image.

## Usage

Once deployed on runpod.io, you can transcribe Hebrew audio either by providing a URL to transcribe (easily supports >1GB payloads, depending on Docker image's free disk space and timeout settings) or by uploading a file (up to ~5-10MB).

### Using the endpoint

Use the ivrit python package.

```
import ivrit

model = ivrit.load_model(engine="runpod", model="ivrit-ai/whisper-large-v3-turbo-ct2", api_key="<your API key>", endpoint_id="<your endpoint ID>")

# Local file transcription (up to ~5MB)
result = model.transcribe(path="<your file>", language="he")

# URL-based transcription
result = model.transcribe(url="<your URL>", language="he")

# Print resulting text
print(result['text'])

# Iterate over segments
for segment in result['segments']:
    print(segment) 
```

Supported models are **ivrit-ai/whisper-large-v3-ct2** and **ivrit-ai/whisper-large-v3-turbo-ct2**.

### Webhook Notifications

The endpoint supports webhook notifications to track transcription progress. Webhooks are sent at three key points:

1. **When transcription starts** - Status: `transcribing`
2. **When transcription completes** - Status: `completed` (includes full transcription)
3. **When an error occurs** - Status: `transcription_failed` or `error` (includes error message)

#### Using Webhooks

To enable webhooks, include `webhook_url` and `recording_id` in your job input:

```python
import ivrit

model = ivrit.load_model(
    engine="runpod", 
    model="ivrit-ai/whisper-large-v3-turbo-ct2", 
    api_key="<your API key>", 
    endpoint_id="<your endpoint ID>"
)

# Transcribe with webhook notifications
result = model.transcribe(
    path="<your file>",
    language="he",
    webhook_url="https://your-backend.com/api/webhook",
    recording_id="unique-recording-id-123"
)
```

#### Webhook Payload Format

Your webhook endpoint will receive POST requests with JSON payloads:

**Transcription Started:**
```json
{
  "recording_id": "unique-recording-id-123",
  "status": "transcribing",
  "timestamp": null
}
```

**Transcription Completed:**
```json
{
  "recording_id": "unique-recording-id-123",
  "status": "completed",
  "transcription": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "transcribed text here",
      ...
    }
  ],
  "timestamp": null
}
```

**Transcription Failed:**
```json
{
  "recording_id": "unique-recording-id-123",
  "status": "transcription_failed",
  "error": "error message here",
  "timestamp": null
}
```

The webhook has a 10-second timeout and errors are logged but won't interrupt the transcription process.

#### Webhook Security

For secure webhook communication, you can set a `WEBHOOK_SECRET` environment variable in your RunPod endpoint configuration. When configured, all webhook requests will include an HMAC-SHA256 signature in the `X-Webhook-Signature` header.

**Setting up the webhook secret:**

1. In your RunPod endpoint settings, add an environment variable:
   - Name: `WEBHOOK_SECRET`
   - Value: Your secret key (e.g., a randomly generated string)

2. In your webhook endpoint, verify the signature:

```python
import hmac
import hashlib
import json

def verify_webhook_signature(payload, signature, secret):
    """Verify the webhook signature"""
    payload_str = json.dumps(payload, sort_keys=True)
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

# In your webhook handler
@app.post("/api/webhook")
async def webhook_handler(request):
    signature = request.headers.get('X-Webhook-Signature')
    payload = await request.json()
    
    if signature:
        secret = os.environ.get('WEBHOOK_SECRET')
        if not verify_webhook_signature(payload, signature, secret):
            return {"error": "Invalid signature"}, 401
    
    # Process the webhook
    recording_id = payload['recording_id']
    status = payload['status']
    # ... handle webhook
```

**Note:** If `WEBHOOK_SECRET` is not set, webhooks will be sent without signatures (less secure but still functional).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
Patreon link: [here](https://www.patreon.com/ivrit_ai).

## License

Our code and model are released under the MIT license.

## Acknowledgements

- [Our long list of data contributors](https://www.ivrit.ai/en/credits)
- Our data annotation volunteers!
