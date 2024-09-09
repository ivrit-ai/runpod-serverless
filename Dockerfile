# Include Python
from python:3.11.1-buster

# Define your working directory
WORKDIR /

# Install runpod
RUN pip install runpod
RUN pip install torch==2.3.1
RUN pip install faster-whisper

RUN python3 -c 'import faster_whisper; m = faster_whisper.WhisperModel("ivrit-ai/faster-whisper-v2-d4")'

# Add your file
ADD infer.py .

ENV LD_LIBRARY_PATH="/usr/local/lib/python3.11/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.11/site-packages/nvidia/cublas/lib"

# Call your file when your container starts
CMD [ "python", "-u", "/infer.py" ]

