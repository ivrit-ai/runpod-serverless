import os
import warnings
from typing import Callable, TYPE_CHECKING

import torch


with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    from pyannote.audio import Pipeline
    
if TYPE_CHECKING:
    from pyannote.core import Annotation


def diarization_pipeline(
    audio_file: str | os.PathLike,
    device: str | torch.device | None = None,
    duration_seconds: int | None = None,
    hook: Callable | None = None,
) -> Annotation:
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device)
    pipeline.to(device)

    print(f"Processing {audio_file} on {device}")
    input_ = audio_file
    if duration_seconds is not None:
        import torchaudio
        waveform, sample_rate = torchaudio.load(audio_file)
        print(f"Trimming waveform to {duration_seconds} seconds")
        max_samples = sample_rate * duration_seconds
        waveform = waveform[:, :max_samples]
        input_ = {"waveform": waveform, "sample_rate": sample_rate}
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", category=UserWarning, message=".*MPEG_LAYER_III.*"
        )
        output = pipeline(input_, hook=hook)
    return output
