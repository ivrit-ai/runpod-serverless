"""
Transcription script for sending local audio files to the RunPod API.

Version: 2025.08.16.p2

Deployment:
    One-click deploy available at:
    https://www.runpod.io/console/hub/ivrit-ai/runpod-serverless

Usage:
    pip install python-dotenv requests
    cd examples
    uv run transcribe.py
"""
import requests
import dotenv
import os
from pathlib import Path
import base64
import json
import time

dotenv.load_dotenv()

API_KEY = os.getenv("RUNPOD_API_KEY") # Example: rpa_<your_api_key>
API_URL = os.getenv("RUNPOD_API_URL") # Example: https://api.runpod.ai/v2/<endpoint_id>

def create_payload(audio_blob, engine='faster-whisper', model='ivrit-ai/whisper-large-v3-turbo-ct2', streaming=False):
    """
    Create the payload for the RunPod API request
    
    Args:
        audio_blob (str): Base64 encoded audio data
        engine (str): Transcription engine ('faster-whisper' or 'stable-whisper')
        model (str): Model name to use for transcription
        streaming (bool): Whether to use streaming mode
    
    Returns:
        dict: Formatted payload for RunPod API
    """
    return {
        "input": {
            "engine": engine,
            "model": model,
            "streaming": streaming,
            "transcribe_args": {
                "blob": audio_blob,
            },
        }
    }

def transcribe(audio_file_path, engine='faster-whisper', model='ivrit-ai/whisper-large-v3-turbo-ct2', streaming=False):
    """
    Transcribe an audio file using RunPod API
    
    Args:
        audio_file_path (str): Path to the audio file
        engine (str): Transcription engine ('faster-whisper' or 'stable-whisper')
        model (str): Model name to use for transcription
        streaming (bool): Whether to use streaming mode
    
    Returns:
        dict: Transcription result from RunPod API
    """
    if not API_KEY:
        raise ValueError("RUNPOD_API_KEY environment variable is required")
    
    if not API_URL:
        raise ValueError("RUNPOD_API_URL environment variable is required")
    
    # Read the audio file and encode it as base64
    with open(audio_file_path, 'rb') as audio_file:
        audio_data = audio_file.read()
        audio_blob = base64.b64encode(audio_data).decode('utf-8')
    
    # Create the request payload
    payload = create_payload(audio_blob, engine, model, streaming)
    
    
    # Make the API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_URL}/run",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"API request failed with status {response.status_code}: {response.text}")
    
    job_data = response.json()
    job_id = job_data.get('id')
    
    if not job_id:
        raise Exception("No job ID received from API")
    
    print(f"Job submitted with ID: {job_id}")
    print("Waiting for transcription to complete...")
    
    # Poll for job completion
    while True:
        time.sleep(2)  # Wait 2 seconds between polls
        
        status_response = requests.get(
            f"{API_URL}/status/{job_id}",
            headers=headers
        )
        
        if status_response.status_code != 200:
            raise Exception(f"Status check failed with status {status_response.status_code}: {status_response.text}")
        
        status_data = status_response.json()
        status = status_data.get('status')
        
        print(f"Job status: {status}")
        
        if status == 'COMPLETED':
            return status_data
        elif status == 'FAILED':
            error_msg = status_data.get('error', 'Unknown error')
            raise Exception(f"Job failed: {error_msg}")
        elif status in ['IN_QUEUE', 'IN_PROGRESS']:
            continue
        else:
            raise Exception(f"Unknown job status: {status}")

def main():
    """Main function to transcribe the audio.opus file"""
    audio_file = Path("./audio.opus")
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file {audio_file} not found")
        return
    
    try:
        print(f"Transcribing {audio_file}...")
        result = transcribe(audio_file, engine='stable-whisper', model='ivrit-ai/whisper-large-v3-turbo-ct2')
        
        print("Transcription completed!")
        print("Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error during transcription: {e}")

if __name__ == "__main__":
    main()

