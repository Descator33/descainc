"""Render an original, seamless pentatonic ambient composition (no samples)."""
from pathlib import Path
import wave
import numpy as np

RATE = 32000
BEAT = 60 / 64
DURATION = 64 * BEAT
COUNT = round(RATE * DURATION)
mix = np.zeros((COUNT, 2), dtype=np.float64)


def add_wrap(sound, start, pan=0, gain=1):
    start = round(start * RATE) % COUNT
    stereo = sound[:, None] * np.array([
        np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    ]) * gain
    first = min(len(stereo), COUNT - start)
    mix[start:start + first] += stereo[:first]
    if first < len(stereo):
        mix[:len(stereo) - first] += stereo[first:]


def pluck(midi, strength):
    frequency = 440 * 2 ** ((midi - 69) / 12)
    t = np.arange(round(RATE * 5.5)) / RATE
    sound = np.zeros_like(t)
    # Rounded attacks, a bright initial string transient, then a warm decay.
    for partial, amplitude in [(1, .68), (2, .2), (3, .075), (4, .025), (6, .012)]:
        decay = 1.45 / partial ** .6
        phase = 2 * np.pi * frequency * partial * (t + .00012 * (1 - np.exp(-t * 35)))
        sound += amplitude * np.sin(phase) * np.exp(-t / decay)
    sound *= (1 - np.exp(-t * 150)) * np.minimum(1, (5.5 - t) / .12)
    return sound * strength


# In-sen pitch collection on D: D, Eb, G, A, C. Space is part of the melody.
melody = [
    (0, 62), (2.5, 69), (4, 67), (6.5, 63), (8, 62),
    (11, 67), (13, 69), (15.5, 72), (18, 69), (20.5, 67),
    (23, 63), (25.5, 62), (29, 57),
    (32, 62), (34.5, 67), (37, 69), (39, 74), (41.5, 72),
    (44, 69), (47, 67), (50, 63), (52.5, 67), (55, 62),
    (58, 57), (61, 62),
]
for i, (beat, midi) in enumerate(melody):
    pan = [-.28, .2, -.1, .32][i % 4]
    sound = pluck(midi, .23 if i % 3 else .28)
    start = beat * BEAT
    add_wrap(sound, start, pan)
    for delay, gain, echo_pan in [(.29, .14, -pan), (.61, .09, pan), (1.11, .045, -pan)]:
        add_wrap(sound, start + delay, echo_pan, gain)

for beat, midi in [(0, 38), (16, 45), (32, 43), (48, 38)]:
    add_wrap(pluck(midi, .15), beat * BEAT, 0)

# Very quiet, periodic sustained harmonics; all phases meet at the loop boundary.
t = np.arange(COUNT) / RATE
breath = .65 + .35 * np.cos(2 * np.pi * t / (16 * BEAT))
for midi, amplitude, pan in [(50, .012, -.25), (57, .008, .25), (62, .004, -.1)]:
    f = round(440 * 2 ** ((midi - 69) / 12) * DURATION) / DURATION
    add_wrap(np.sin(2 * np.pi * f * t) * amplitude * breath, 0, pan)

# Short, diffuse room reflections wrap around, preserving the musical loop.
dry = mix.copy()
for delay, gain in [(.071, .08), (.137, .065), (.193, .045), (.347, .03)]:
    mix += np.roll(dry[:, ::-1], round(delay * RATE), axis=0) * gain
mix -= mix.mean(axis=0)
mix *= .48 / np.max(np.abs(mix))
output = Path(__file__).resolve().parents[1] / 'output' / 'music-original.wav'
output.parent.mkdir(exist_ok=True)
with wave.open(str(output), 'wb') as wav:
    wav.setnchannels(2)
    wav.setsampwidth(2)
    wav.setframerate(RATE)
    wav.writeframes((mix * 32767).astype('<i2').tobytes())
print(f'Original composition: {DURATION:.0f}s, stereo, seamless wrap. {output}')
