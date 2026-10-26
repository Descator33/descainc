"""Export the second rendered cycle with quiet, device-independent headroom."""
from pathlib import Path
import subprocess
import wave
import numpy as np

root = Path(__file__).resolve().parents[1]
quiet = root / 'output' / 'soft-piano-quiet.wav'
subprocess.run([
    'ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', '60',
    '-i', str(root / 'output' / 'soft-piano-render.wav'), '-t', '60',
    '-af', 'loudnorm=I=-32:TP=-3:LRA=5', '-ar', '32000',
    '-c:a', 'pcm_s16le', '-y', str(quiet)
], check=True)
with wave.open(str(quiet)) as audio:
    params = audio.getparams()
    samples = np.frombuffer(audio.readframes(audio.getnframes()), dtype='<i2').astype(float) / 32768
samples *= min(1, .10 / np.max(np.abs(samples)))
with wave.open(str(quiet), 'wb') as audio:
    audio.setparams(params)
    audio.writeframes(np.round(samples * 32767).astype('<i2').tobytes())
subprocess.run([
    'ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(quiet),
    '-codec:a', 'libmp3lame', '-q:a', '5',
    '-metadata', 'title=Melodia soffice — Desca Inc.', '-metadata', 'artist=Desca Inc.',
    '-y', str(root / 'dist' / 'assets' / 'melodia-soffice.mp3')
], check=True)
print('Exported quiet piano, 60 seconds; peak capped at -20 dBFS before encoding.')
