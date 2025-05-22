# Include Python
FROM pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime

# Define your working directory
WORKDIR /

# Configure LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH="/opt/conda/lib/python3.11/site-packages/nvidia/cudnn/lib:/opt/conda/lib/python3.11/site-packages/nvidia/cublas/lib"

# Install runpod
RUN pip install runpod
RUN pip install faster-whisper==1.1.1
RUN pip install stable-ts==2.18.3

RUN python3 -c 'import faster_whisper; m = faster_whisper.WhisperModel("ivrit-ai/whisper-large-v3-turbo-ct2")'

# Add your file
ADD infer.py .

# Call your file when your container starts
CMD [ "python", "-u", "/infer.py" ]

