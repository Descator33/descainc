"""Original sparse major-pentatonic chimes, without ambient noise."""
from pathlib import Path
import wave
import numpy as np

RATE = 32000
DURATION = 60
COUNT = RATE * DURATION
mix = np.zeros((COUNT, 2))



def add_wrap(sound, start, pan=0, gain=1):
    start = round(start * RATE) % COUNT
    stereo = sound[:, None] * np.array([
        np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    ]) * gain
    first = min(len(stereo), COUNT - start)
    mix[start:start + first] += stereo[:first]
    if first < len(stereo):
        mix[:len(stereo) - first] += stereo[first:]


def chime(midi):
    f = 440 * 2 ** ((midi - 69) / 12)
    local = np.arange(RATE * 7) / RATE
    sound = np.zeros_like(local)
    # A rounded, bamboo-like chime rather than a sharp metallic bell.
    for ratio, amplitude, decay in [(1, .85, 2.2), (2.002, .12, 1.3), (3, .025, .65)]:
        sound += amplitude * np.sin(2 * np.pi * f * ratio * local) * np.exp(-local / decay)
    sound *= (1 - np.exp(-local / .055)) * np.minimum(1, (7 - local) / .3)
    return sound


# D-major pentatonic: open, gently ascending fragments with generous silence.
notes = [(2.4, 74), (6.1, 76), (10.8, 78), (17.3, 81),
         (22.6, 78), (29.4, 76), (35.2, 74), (40.7, 78),
         (44.9, 81), (50.3, 83), (55.1, 81)]
for i, (start, midi) in enumerate(notes):
    note = chime(midi)
    pan = [-.32, .24, -.08, .35][i % 4]
    strength = [.065, .052, .058][i % 3]
    add_wrap(note, start, pan, strength)
    for delay, gain in [(.19, .12), (.43, .075), (.79, .04), (1.31, .022)]:
        add_wrap(note, start + delay, -pan, strength * gain)

mix -= mix.mean(axis=0)
# Preserve the chimes' previous gain when removing the wind layer.
mix *= 3.639641451872925
peak = np.max(np.abs(mix))
if peak > .38:
    mix *= .38 / peak
output = Path(__file__).resolve().parents[1] / 'output' / 'music-notes.wav'
output.parent.mkdir(exist_ok=True)
with wave.open(str(output), 'wb') as wav:
    wav.setnchannels(2)
    wav.setsampwidth(2)
    wav.setframerate(RATE)
    wav.writeframes((mix * 32767).astype('<i2').tobytes())
print(f'Original chimes (no wind): {DURATION}s, stereo, seamless loop. {output}')
