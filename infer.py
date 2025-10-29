import dataclasses
import runpod
import ivrit
import types
import logging
import requests
import json
import hmac
import hashlib
import os

# Maximum size for grouped arrays (in characters).
# This ensures we are below the maximum size of an item in a RunPod stream.
MAX_RUNPOD_STREAM_ELEMENT_SIZE = 500000

# Global variables to track the currently loaded model
current_model = None

def extract_transcription_text(segments):
    """Extract plain text from transcription segments"""
    if not segments:
        return ""
    
    text_parts = []
    for segment in segments:
        if isinstance(segment, dict) and 'text' in segment:
            text_parts.append(segment['text'])
        elif isinstance(segment, str):
            text_parts.append(segment)
    
    return ' '.join(text_parts).strip()

def send_webhook(webhook_url, recording_id, status, transcription_text=None, error=None):
    """
    Send webhook notification to Next.js backend when transcription completes or fails
    
    Args:
        webhook_url: The URL to send the webhook to
        recording_id: Unique identifier for the recording
        status: Status of the transcription ('started', 'completed', 'error')
        transcription_text: The transcription result (only for 'completed' status)
        error: Error message (only for 'error' status)
    """
    if not webhook_url:
        return
    
    payload = {
        'recording_id': recording_id,
        'status': status,
        'timestamp': None  # You might want to add a timestamp here
    }
    
    if transcription_text is not None:
        payload['transcription'] = transcription_text
    
    if error is not None:
        payload['error'] = error
    
    # Get webhook secret from environment variable
    webhook_secret = os.environ.get('WEBHOOK_SECRET', '')
    
    headers = {'Content-Type': 'application/json'}
    
    # Generate HMAC signature if secret is provided
    if webhook_secret:
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        headers['X-Webhook-Signature'] = signature
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        logging.info(f"Webhook sent successfully to {webhook_url} for recording {recording_id} with status {status}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send webhook to {webhook_url}: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error sending webhook: {str(e)}")

def transcribe(job):
    engine = job['input'].get('engine', 'faster-whisper')
    model_name = job['input'].get('model', None)
    is_streaming = job['input'].get('streaming', False)
    
    # Get webhook parameters
    webhook_url = job['input'].get('webhook_url', None)
    recording_id = job['input'].get('recording_id', None)

    if not engine in ['faster-whisper', 'stable-whisper']:
        error_msg = f"engine should be 'faster-whisper' or 'stable-whisper', but is {engine} instead."
        send_webhook(webhook_url, recording_id, 'transcription_failed', error=error_msg)
        yield { "error" : error_msg }
        return

    if not model_name:
        error_msg = "Model not provided."
        send_webhook(webhook_url, recording_id, 'transcription_failed', error=error_msg)
        yield { "error" : error_msg }
        return

    # Get the API key from the job input
    api_key = job['input'].get('api_key', None)

    # Extract transcribe_args from job input
    transcribe_args = job['input'].get('transcribe_args', None)

    # Validate that transcribe_args contains either blob or url
    if not transcribe_args:
        error_msg = "transcribe_args field not provided."
        send_webhook(webhook_url, recording_id, 'transcription_failed', error=error_msg)
        yield { "error" : error_msg }
        return
    
    if not ('blob' in transcribe_args or 'url' in transcribe_args):
        error_msg = "transcribe_args must contain either 'blob' or 'url' field."
        send_webhook(webhook_url, recording_id, 'transcription_failed', error=error_msg)
        yield { "error" : error_msg }
        return

    # Send webhook notification that transcription has started
    send_webhook(webhook_url, recording_id, 'transcribing')

    try:
        stream_gen = transcribe_core(engine, model_name, transcribe_args)

        if is_streaming:
            result = []
            for entry in stream_gen:
                result.extend(entry if isinstance(entry, list) else [entry])
                yield entry
            transcription_text = extract_transcription_text(result)
            # Send completion webhook with full transcription
            send_webhook(webhook_url, recording_id, 'transcribed', transcription_text=transcription_text)
        else:
            result = [entry for entry in stream_gen]
            # Flatten the result if needed
            flattened_result = []
            for entry in result:
                if isinstance(entry, list):
                    flattened_result.extend(entry)
                else:
                    flattened_result.append(entry)
            transcription_text = extract_transcription_text(flattened_result)
            # Send completion webhook with full transcription
            send_webhook(webhook_url, recording_id, 'transcribed', transcription_text=transcription_text)
            yield { 'result' : result }
    except Exception as e:
        error_msg = str(e)
        send_webhook(webhook_url, recording_id, 'transcription_failed', error=error_msg)
        yield { "error" : error_msg }

def transcribe_core(engine, model_name, transcribe_args):
    print('Transcribing...')
    
    global current_model

    different_model = (not current_model) or (current_model.engine != engine or current_model.model != model_name)

    if different_model:
        print(f'Loading new model: {engine} with {model_name}')
        current_model = ivrit.load_model(engine=engine, model=model_name, local_files_only=True)
    else:
        print(f'Reusing existing model: {engine} with {model_name}')

    diarize = transcribe_args.get('diarize', False)

    if diarize:
        res = current_model.transcribe(**transcribe_args)

        segs = res['segments']
    else:
        transcribe_args['stream'] = True 
        segs = current_model.transcribe(**transcribe_args)

    # Check if segs is a generator
    if isinstance(segs, types.GeneratorType):
        # For generators, yield results one by one as an array of one value
        for s in segs:
            yield [dataclasses.asdict(s)]
    else:
        # For non-generators, group multiple consecutive members into larger arrays
        # ensuring their total size is less than MAX_RUNPOD_STREAM_ELEMENT_SIZE
        current_group = []
        current_size = 0
        
        for s in segs:
            seg_dict = dataclasses.asdict(s)
            seg_size = len(str(seg_dict))
            
            # If adding this segment would exceed the max size, yield current group
            if current_group and (current_size + seg_size > MAX_RUNPOD_STREAM_ELEMENT_SIZE):
                yield current_group
                current_group = []
                current_size = 0
            
            # Add segment to current group
            current_group.append(seg_dict)
            current_size += seg_size
        
        # Yield any remaining segments in the final group
        if current_group:
            yield current_group

runpod.serverless.start({"handler": transcribe, "return_aggregate_stream": True})

