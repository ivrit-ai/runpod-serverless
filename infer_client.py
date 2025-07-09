# Set up runpod package, and API key
import base64
import os
import requests
import time

import runpod

IN_QUEUE_TIMEOUT = 300
MAX_STREAM_TIMEOUTS = 5
RUNPOD_MAX_PAYLOAD_LEN = 10 * 1024 * 1024

def transcribe(model, payload_type, path_or_url):  
    if not payload_type in ["blob", "url"]:
        raise 1

    payload = {
        "input": {
            "type": payload_type,
            "model": model,
            "streaming": True
        }
    }

    if payload_type == "blob":
        audio_data = open(path_or_url, 'rb').read()
        payload["input"]["data"] = base64.b64encode(audio_data).decode('utf-8')
    else:
        payload["input"]["url"] = path_or_url

    if len(str(payload)) > RUNPOD_MAX_PAYLOAD_LEN:
        return {"error": f"Payload length is {len(str(payload))}, exceeding max payload length of {RUNPOD_MAX_PAYLOAD_LEN}."}

    # Configure runpod endpoint, and execute
    runpod.api_key = os.environ["RUNPOD_API_KEY"]
    ep = runpod.Endpoint(os.environ["RUNPOD_ENDPOINT_ID"])
    run_request = ep.run(payload)

    # Wait for task to be queued.
    # Max wait time is IN_QUEUE_WAIT_TIME seconds.
    for i in range(IN_QUEUE_TIMEOUT):
        if run_request.status() == "IN_QUEUE":
            time.sleep(1)
            continue

        break

    # Collect streaming results.
    segments = []

    timeouts = 0
    while True:
        try:
            for segment in run_request.stream():
                if "error" in segment:
                    return segment

                segments.append(segment)

            return segments

        except requests.exceptions.ReadTimeout as e:
            timeouts += 1
            if timeouts > MAX_STREAM_TIMEOUTS:
                return {"error": f"Number of request.stream() timeouts exceeded the maximum ({MAX_STREAM_TIMEOUTS})."}
            pass

        except Exception as e:
            run_request.cancel()
            return {"error": f"Exception during run_request.stream(): {e}"}

