# Include Python
FROM pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime

# Define your working directory
WORKDIR /

# Configure LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH="/opt/conda/lib/python3.11/site-packages/nvidia/cudnn/lib:/opt/conda/lib/python3.11/site-packages/nvidia/cublas/lib"

# Install relevant packages 
RUN apt update
RUN apt install -y ffmpeg

# Install python packages
RUN pip3 install ivrit[all]==0.1.8 torch==2.4.1 huggingface-hub==0.36.0 runpod
RUN pip3 install requests

RUN python3 -c 'import faster_whisper; m = faster_whisper.WhisperModel("ivrit-ai/whisper-large-v3-turbo-ct2")'
# RUN python3 -c 'import faster_whisper; m = faster_whisper.WhisperModel("ivrit-ai/yi-whisper-large-v3-turbo-ct2")'
RUN python3 -c 'import faster_whisper; m = faster_whisper.WhisperModel("large-v3-turbo")'
RUN python3 -c 'import pyannote.audio; p = pyannote.audio.Pipeline.from_pretrained("ivrit-ai/pyannote-speaker-diarization-3.1")'
RUN python3 -c 'from speechbrain.inference.speaker import EncoderClassifier; EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")'

# Add your file
ADD infer.py .

# Call your file when your container starts
CMD [ "python", "-u", "/infer.py" ]

