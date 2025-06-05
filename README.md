# runpod-serverless

[![RunPod](https://api.runpod.io/badge/ivrit-ai/runpod-serverless)](https://www.runpod.io/console/hub/ivrit-ai/runpod-serverless)

A template for transcribing Hebrew audio using runpod.io serverless infrastructure.

Note: if you register at [runpod.io], we'd like to ask you to consider using our [referral link](https://runpod.io/?ref=06octndf).
It provides us with more credits, which we can then use to provide better services.

## Description

This project provides a serverless solution for transcribing Hebrew audio files. It leverages runpod.io's infrastructure to process audio files efficiently and return transcriptions.
It is part of the [ivrit.ai](https://ivrit.ai) non-profit project.

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

Once deployed on runpod.io, you can transcribe Hebrew audio either by providing a URL to transcribe (up to 200MB), or by uploading a file (up to 10MB).

### URL-based transcription

```
import runpod
import base64

# 1. model: ivrit-ai/whisper-large-v3-ct2, ivrit-ai/whisper-large-v3-turbo-ct2
# 2. engine: faster-whisper, stable-whisper
payload = { 'type' : 'url', 'url' : 'https://your-audio-url', 'model' : 'ivrit-ai/whisper-large-v3-turbo-ct2', 'engine' : 'faster-whisper' }

runpod.api_key = '<Your runpod.io API key>'
ep = runpod.Endpoint("<endpoint key>")
res = ep.run_sync(payload)
```

### File upload

```
import runpod
import base64

mp3_data = open('<file>.mp3', 'rb').read()
data = base64.b64encode(mp3_data).decode('utf-8')

# 1. model: ivrit-ai/whisper-large-v3-ct2, ivrit-ai/whisper-large-v3-turbo-ct2
# 2. engine: faster-whisper, stable-whisper
payload = { 'type' : 'blob', 'data' : data, 'model' : 'ivrit-ai/whisper-large-v3-turbo-ct2', 'engine' : 'faster-whisper' }

runpod.api_key = '<Your runpod.io API key>'
ep = runpod.Endpoint("<endpoint key>")
res = ep.run_sync(payload)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Our code and model are released under the MIT license.

## Acknowledgements

- [Our long list of data contributors](https://www.ivrit.ai/en/credits)
- Our data annotation volunteers!
