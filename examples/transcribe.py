"""
Transcription script that reads a local audio file and sends it to RunPod API for transcription

Usage:
    cd examples
    uv run transcribe.py
"""
import requests
import dotenv
import os
import base64
import json
import time

dotenv.load_dotenv()

API_KEY = os.getenv("RUNPOD_API_KEY")
ENDPOINT_ID = os.getenv("RUNPOD_API_URL")

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
    
    if not ENDPOINT_ID:
        raise ValueError("RUNPOD_API_URL environment variable is required")
    
    # Read the audio file and encode it as base64
    with open(audio_file_path, 'rb') as audio_file:
        audio_data = audio_file.read()
        audio_blob = base64.b64encode(audio_data).decode('utf-8')
    
    # Prepare the request payload
    payload = {
        "input": {
            "engine": engine,
            "model": model,
            "streaming": streaming,
            "transcribe_args": {
                "blob": audio_blob,
            },
        }
    }
    
    
    # Make the API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{ENDPOINT_ID}/run",
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
            f"{ENDPOINT_ID}/status/{job_id}",
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
    audio_file = "./audio.opus"
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file {audio_file} not found")
        return
    
    try:
        print(f"Transcribing {audio_file}...")
        result = transcribe(audio_file)
        
        print("Transcription completed!")
        print("Result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error during transcription: {e}")

if __name__ == "__main__":
    main()

