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

Copy the infer_client.py file, then invoke transcription using it:

```
import infer_client
import os

os["environ"]["RUNPOD_API_KEY"] = "<your API key>"
os["environ"]["RUNPOD_ENDPOINT_ID"] = "<your endpoint ID>"

# Local file transcription (up to ~5MB)
local_segments = infer_client.transcribe("ivrit-ai/whisper-large-v3-turbo-ct2", "blob", "<your file>")

# URL-based transcription
url_segments = infer_client.transcribe("ivrit-ai/whisper-large-v3-turbo-ct2", "url", "<your URL>")
```

Supported models are **ivrit-ai/whisper-large-v3-ct2** and **ivrit-ai/whisper-large-v3-turbo-ct2**.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
Patreon link: [here](https://www.patreon.com/ivrit_ai).

## License

Our code and model are released under the MIT license.

## Acknowledgements

- [Our long list of data contributors](https://www.ivrit.ai/en/credits)
- Our data annotation volunteers!
