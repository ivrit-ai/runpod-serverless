import runpod
import ivrit
import jsonpickle

# Global variables to track the currently loaded model
current_model = None

def transcribe(job):
    engine = job['input'].get('engine', 'faster-whisper')
    model_name = job['input'].get('model', 'ivrit-ai/whisper-large-v3-turbo-ct2')
    is_streaming = job['input'].get('streaming', False)

    if not engine in ['faster-whisper', 'stable-whisper']:
        yield { "error" : f"engine should be 'faster-whsiper' or 'stable-whisper', but is {engine} instead." }

    # Get the API key from the job input
    api_key = job['input'].get('api_key', None)

    # Extract transcribe_args from job input
    transcribe_args = job['input'].get('transcribe_args', None)

    # Validate that transcribe_args contains either blob or url
    if not transcribe_args:
        yield { "error" : "transcribe_args field not provided." }
    
    if not ('blob' in transcribe_args or 'url' in transcribe_args):
        yield { "error" : "transcribe_args must contain either 'blob' or 'url' field." }

    stream_gen = transcribe_core(engine, model_name, transcribe_args)

    if is_streaming:
        for entry in stream_gen:
            yield entry
    else:
        result = [entry for entry in stream_gen]
        yield { 'result' : result }

def transcribe_core(engine, model_name, transcribe_args):
    print('Transcribing...')
    
    global current_model

    different_model = (not current_model) or (current_model.engine != engine or current_model.model != model_name)

    if different_model:
        print(f'Loading new model: {engine} with {model_name}')
        current_model = ivrit.load_model(engine=engine, model=model_name, local_files_only=True)
    else:
        print(f'Reusing existing model: {engine} with {model_name}')

    segs = current_model.transcribe(**transcribe_args, stream=True)

    for s in segs:
        yield jsonpickle.encode(s)

runpod.serverless.start({"handler": transcribe, "return_aggregate_stream": True})

