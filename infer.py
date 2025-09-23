import dataclasses
import runpod
import ivrit
import types
import logging

# Maximum size for grouped arrays (in characters).
# This ensures we are below the maximum size of an item in a RunPod stream.
MAX_RUNPOD_STREAM_ELEMENT_SIZE = 500000

# Global variables to track the currently loaded model
current_model = None

def transcribe(job):
    engine = job['input'].get('engine', 'faster-whisper')
    model_name = job['input'].get('model', None)
    is_streaming = job['input'].get('streaming', False)

    if not engine in ['faster-whisper', 'stable-whisper']:
        yield { "error" : f"engine should be 'faster-whisper' or 'stable-whisper', but is {engine} instead." }

    if not model_name:
        yield { "error" : "Model not provided." }

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

