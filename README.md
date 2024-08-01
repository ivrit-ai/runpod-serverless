# runpod-serverless

A template for transcribing Hebrew audio using runpod.io serverless infrastructure.

## Description

This project provides a serverless solution for transcribing Hebrew audio files. It leverages runpod.io's infrastructure to process audio files efficiently and return transcriptions.
It is part of the [ivrit.ai](https://ivrit.ai) non-profit project.

## Contents

- `Dockerfile`: Used to create the Docker image for the serverless function.
- `infer.py`: The main script that handles the transcription process, placed inside the Docker image.

## Building your own Docker image

1. Clone this repository:

```
git clone https://github.com/yourusername/runpod-serverless.git
cd runpod-serverless
```

2. Build the Docker image:

```
docker build -t runpod-serverless .
```

3. Push the image to a public Docker repository:

a. If you haven't already, create an account on [Docker Hub](https://hub.docker.com/).

b. Log in to Docker Hub from your command line:
   ```
   docker login
   ```

c. Tag your image with your Docker Hub username:
   ```
   docker tag runpod-serverless yourusername/runpod-serverless:latest
   ```

d. Push the image to Docker Hub:
   ```
   docker push yourusername/runpod-serverless:latest
   ```

4. Set up a serverless function on runpod.io using the pushed image.

## Usage

Once deployed on runpod.io, you can send Hebrew audio files to the serverless function for transcription. The exact usage will depend on your specific implementation in `infer.py`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Our code and model are released under the MIT license.

## Acknowledgements

- [Our long list of data contributors](https://www.ivrit.ai/en/credits)
- Our data annotation volunteers!
