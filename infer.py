import runpod

import base64
import faster_whisper
import tempfile

model_name = 'ivrit-ai/faster-whisper-v2-d3-e3'
model = faster_whisper.WhisperModel(model_name, device='cuda')


def transcribe(job):
    print(job.keys())
    print(job)

    result = process_task(job['input']['data'])

    return { 'text' : job, 'result' : result }

def process_task(data):
    print('Transcribing...')

    # Implement your task processing logic here
    # For example, execute Python code based on task_type and data
    # Decode the base64-encoded MP3 data
    with tempfile.TemporaryDirectory() as d:
        mp3_bytes = base64.b64decode(data)
        open(f'{d}/audio.mp3', 'wb').write(mp3_bytes)

        ret = { 'segments' : [] }

        segs, dummy = model.transcribe(f'{d}/audio.mp3', language='he')
        for s in segs:
            print(s)
            seg = { 'id' : s.id, 'seek' : s.seek, 'start' : s.start, 'end' : s.end, 'text' : s.text, 'avg_logprob' : s.avg_logprob, 'compression_ratio' : s.compression_ratio, 'no_speech_prob' : s.no_speech_prob }
            ret['segments'].append(seg)

        return ret

runpod.serverless.start({"handler": transcribe})

