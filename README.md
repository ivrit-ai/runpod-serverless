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

#### Output Options

The `transcribe()` method accepts an `output_options` parameter (dictionary) to control the detail level of the output:

```
result = model.transcribe(
    path="<your file>", 
    language="he",
    output_options={
        "word_timestamps": False,  # Disable word-level timestamps
        "extra_data": False         # Disable extra metadata
    }
)
```

Setting both `word_timestamps` and `extra_data` to `False` significantly reduces the output length, which is important when using non-streaming mode as it minimizes response payload size and improves performance.

#### Diarization (Speaker Identification)

For diarization (identifying different speakers), use the `stable-whisper` core engine:

```
import ivrit

model = ivrit.load_model(
    engine="runpod", 
    model="ivrit-ai/whisper-large-v3-turbo-ct2", 
    api_key="<your API key>", 
    endpoint_id="<your endpoint ID>",
    core_engine="stable-whisper"
)

# Transcribe with diarization enabled
result = model.transcribe(
    path="<your file>", 
    language="he",
    diarize=True
)

# Results will include speaker labels in segments
for segment in result['segments']:
    print(f"Speakers {segment.speakers}: {segment['text']}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
Patreon link: [here](https://www.patreon.com/ivrit_ai).

## License

Our code and model are released under the MIT license.

## Acknowledgements

- [Our long list of data contributors](https://www.ivrit.ai/en/credits)
- Our data annotation volunteers!
